"""Regression tests for the local AI image editing bridge."""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
