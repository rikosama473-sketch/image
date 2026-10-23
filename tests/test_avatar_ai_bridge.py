"""Regression tests for the local AI image editing bridge."""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import sys
import threading
import types
import unittest
from http.client import HTTPConnection
from io import BytesIO
from pathlib import Path
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "avatar-maker" / "ai_edit_server.py"
SPEC = importlib.util.spec_from_file_location("avatar_ai_edit_server", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


def data_url(mime: str, data: bytes) -> str:
    return "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")


class DataUrlValidationTests(unittest.TestCase):
    def test_accepts_png_signature(self):
        value = data_url("image/png", b"\x89PNG\r\n\x1a\nsample")
        self.assertEqual(bridge.validate_data_url(value, "test"), value)

    def test_accepts_jpeg_signature(self):
        value = data_url("image/jpeg", b"\xff\xd8\xffsample")
        self.assertEqual(bridge.validate_data_url(value, "test"), value)

    def test_accepts_webp_signature(self):
        value = data_url("image/webp", b"RIFF\x04\x00\x00\x00WEBPsample")
        self.assertEqual(bridge.validate_data_url(value, "test"), value)

    def test_rejects_mismatched_signature(self):
        with self.assertRaisesRegex(ValueError, "no coincide"):
            bridge.validate_data_url(data_url("image/png", b"not a png"), "test")

    def test_rejects_non_image_mime_and_invalid_base64(self):
        with self.assertRaises(ValueError):
            bridge.validate_data_url("data:image/svg+xml;base64,PHN2Zz4=", "test")
        with self.assertRaises(ValueError):
            bridge.validate_data_url("data:image/png;base64,%%%not-base64%%%", "test")

    def test_mask_accepts_png_and_rejects_other_formats(self):
        png = data_url("image/png", b"\x89PNG\r\n\x1a\nmask")
        self.assertEqual(bridge.validate_mask_data_url(png), png)
        jpeg = data_url("image/jpeg", b"\xff\xd8\xffmask")
        with self.assertRaisesRegex(ValueError, "debe ser PNG"):
            bridge.validate_mask_data_url(jpeg)


class AIParameterValidationTests(unittest.TestCase):
    def test_variants_accept_only_one_to_four_integers(self):
        for value in (1, 2, 3, 4):
            with self.subTest(value=value):
                self.assertEqual(bridge.validate_variants(value), value)
        for value in (0, 5, -1, True, False, "2", 2.0, None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    bridge.validate_variants(value)

    def test_standard_quality_levels_for_supported_models(self):
        for model in ("gpt-image-2", "gpt-image-1.5"):
            for quality in ("low", "medium", "high"):
                with self.subTest(model=model, quality=quality):
                    self.assertEqual(bridge.validate_quality(model, quality), quality)

    def test_xhigh_and_max_are_limited_to_image_25_models(self):
        for model in ("gpt-image-2.5-sunburst", "gpt-image-2.5-flare"):
            for quality in ("xhigh", "max"):
                with self.subTest(model=model, quality=quality):
                    self.assertEqual(bridge.validate_quality(model, quality), quality)
        for model in ("gpt-image-2", "gpt-image-1.5"):
            for quality in ("xhigh", "max"):
                with self.subTest(model=model, quality=quality):
                    with self.assertRaisesRegex(ValueError, "solo está disponible"):
                        bridge.validate_quality(model, quality)

    def test_unknown_quality_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "calidad"):
            bridge.validate_quality("gpt-image-2.5-sunburst", "ultra")


class LocalBridgeHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = bridge.ThreadingHTTPServer(("127.0.0.1", 0), bridge.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body: bytes | None = None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        status = response.status
        content = response.read().decode("utf-8")
        conn.close()
        return status, content

    def test_status_does_not_expose_api_key(self):
        old = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "unit-test-secret-do-not-return"
        try:
            status, content = self.request("GET", "/api/status")
            self.assertEqual(status, 200)
            parsed = json.loads(content)
            self.assertTrue(parsed["api_key_configured"])
            self.assertNotIn("unit-test-secret-do-not-return", content)
            self.assertEqual(parsed["key_storage"], "environment_only")
        finally:
            if old is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old

    def test_without_api_key_still_returns_controlled_error(self):
        old = os.environ.pop("OPENAI_API_KEY", None)
        try:
            status, content = self.request("POST", "/api/ai-edit", b"{}")
            self.assertEqual(status, 503)
            self.assertIn("OPENAI_API_KEY", json.loads(content)["error"])
        finally:
            if old is not None:
                os.environ["OPENAI_API_KEY"] = old

    def test_local_anime_cutout_preserves_canvas_and_requires_real_alpha(self):
        source = Image.new("RGBA", (64, 64), (180, 130, 90, 255))
        source_buffer = BytesIO()
        source.save(source_buffer, format="PNG")
        output_buffer = BytesIO()
        output = Image.new("RGBA", (64, 64), (180, 130, 90, 255))
        for y in range(64):
            for x in range(64):
                if x < 8 or x >= 56 or y < 8 or y >= 56:
                    output.putpixel((x, y), (0, 0, 0, 0))
        output.save(output_buffer, format="PNG")
        calls = {"session": 0, "remove": 0, "model": None}

        def fake_new_session(model):
            calls["session"] += 1
            calls["model"] = model
            return object()

        def fake_remove(image_bytes, **kwargs):
            calls["remove"] += 1
            self.assertTrue(kwargs.get("decontaminate"))
            self.assertTrue(kwargs.get("force_return_bytes"))
            return output_buffer.getvalue()

        fake_rembg = types.SimpleNamespace(new_session=fake_new_session, remove=fake_remove)
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            with mock.patch.dict(sys.modules, {"rembg": fake_rembg}):
                status, content = self.request("POST", "/api/remove-background", json.dumps({
                    "model": "isnet-anime",
                    "image_data_url": data_url("image/png", source_buffer.getvalue()),
                }).encode("utf-8"))
            self.assertEqual(status, 200, content)
            payload = json.loads(content)
            self.assertEqual(payload["engine"], "rembg-local")
            self.assertTrue(payload["source_artwork_preserved"])
            self.assertTrue(payload["edge_decontamination"])
            self.assertEqual((payload["width"], payload["height"]), (64, 64))
            result = Image.open(BytesIO(base64.b64decode(payload["image_base64"]))).convert("RGBA")
            self.assertEqual(result.size, (64, 64))
            self.assertEqual(result.getchannel("A").getpixel((0, 0)), 0)
            self.assertEqual(result.getchannel("A").getpixel((32, 32)), 255)
            self.assertEqual(calls["model"], "isnet-anime")
            self.assertEqual(calls["remove"], 1)
        finally:
            bridge._CUTOUT_SESSIONS.pop("isnet-anime", None)
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key

    def test_local_cutout_rejects_unknown_model(self):
        png = Image.new("RGB", (64, 64), "white")
        buffer = BytesIO()
        png.save(buffer, format="PNG")
        status, content = self.request("POST", "/api/remove-background", json.dumps({
            "model": "not-a-model",
            "image_data_url": data_url("image/png", buffer.getvalue()),
        }).encode("utf-8"))
        self.assertEqual(status, 400)
        self.assertIn("Elegí el modelo local", json.loads(content)["error"])


if __name__ == "__main__":
    unittest.main()
