from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml"))
import character_editor_server as editor  # noqa: E402


class AppRootTests(unittest.TestCase):
    def test_frozen_bundle_uses_pyinstaller_extraction_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / "tools" / "character-editor").mkdir(parents=True)
            root = editor.resolve_app_root(Path("X:/ignored/ml/script.py"), frozen_root=bundle)
            self.assertEqual(root, bundle.resolve())
            self.assertEqual(root / "tools" / "character-editor", bundle / "tools" / "character-editor")


class AssetCatalogTests(unittest.TestCase):
    def test_index_and_search_are_paginated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("red-hair.png", "blue-hair.webp", "arm.jpg", "not-image.txt"):
                (root / name).write_bytes(b"fixture")
            catalog = editor.AssetCatalog(root)
            self.assertEqual(len(catalog.items), 3)
            page = catalog.list_assets("hair", offset=0, limit=1)
            self.assertEqual(page["total"], 2)
            self.assertEqual(len(page["items"]), 1)
            self.assertTrue(page["items"][0]["name"].endswith((".png", ".webp")))

    def test_hidden_directories_and_symlinks_are_not_followed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "visible.png").write_bytes(b"visible")
            hidden = root / ".private"
            hidden.mkdir()
            (hidden / "secret.png").write_bytes(b"secret")
            outside = root.parent / (root.name + "-outside.png")
            outside.write_bytes(b"outside")
            link = root / "outside.png"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                link = None
            try:
                catalog = editor.AssetCatalog(root)
                self.assertEqual({item["path"] for item in catalog.items}, {"visible.png"})
                if link is not None:
                    self.assertIsNone(catalog.safe_path("outside.png"))
            finally:
                outside.unlink(missing_ok=True)

    def test_path_traversal_and_non_image_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "image.png").write_bytes(b"png")
            (root / "note.txt").write_text("not an image", encoding="utf-8")
            catalog = editor.AssetCatalog(root)
            self.assertIsNone(catalog.safe_path("../note.txt"))
            self.assertIsNone(catalog.safe_path("note.txt"))
            self.assertIsNotNone(catalog.safe_path("image.png"))

    def test_packaged_smoke_test_passes_without_model_weights(self) -> None:
        self.assertEqual(editor.run_self_test(), 0)

    def test_invalid_pagination_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            catalog = editor.AssetCatalog(Path(directory))
            for kwargs in ({"offset": -1}, {"limit": 0}, {"limit": 97}, {"query": "x" * 201}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    catalog.list_assets(**kwargs)


class HTTPHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "sample.png").write_bytes(b"sample-bytes")
        self.server = editor.CharacterEditorHTTPServer(("127.0.0.1", 0), editor.AssetCatalog(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def get(self, path: str):
        with urllib.request.urlopen(self.base + path, timeout=3) as response:
            return response.status, response.headers, response.read()

    def test_assets_api_returns_paths_not_private_prompts(self) -> None:
        status, headers, content = self.get("/api/assets?query=sample&limit=4")
        data = json.loads(content)
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["path"], "sample.png")
        self.assertIn("Content-Security-Policy", headers)

    def test_asset_endpoint_serves_only_catalogued_images(self) -> None:
        status, _, content = self.get("/api/asset?path=sample.png")
        self.assertEqual(status, 200)
        self.assertEqual(content, b"sample-bytes")
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/asset?path=../README.md")
        self.assertEqual(caught.exception.code, 404)

    def test_upload_endpoints_are_disabled(self) -> None:
        request = urllib.request.Request(self.base + "/api/assets", data=b'{"file":"anything"}', headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 405)

    def test_editor_html_is_served(self) -> None:
        status, headers, content = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn(b"Editor modular de personajes", content)


if __name__ == "__main__":
    unittest.main()
