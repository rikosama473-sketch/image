from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_asset_packs import PACKS, _validated_members, safe_extract_zip  # noqa: E402


class FetchAssetPacksTests(unittest.TestCase):
    def test_only_original_https_sources_are_allowlisted(self) -> None:
        self.assertEqual(set(PACKS), {"anime-portraits", "modular-64x96", "visual-novel-characters"})
        for pack in PACKS.values():
            self.assertTrue(pack["url"].startswith("https://opengameart.org/"))
            self.assertTrue(pack["source_page"].startswith(("https://opengameart.org/content/", "https://opengameart.org/node/")))
            if pack["expected_bytes"] is not None:
                self.assertGreater(pack["expected_bytes"], 0)

    def test_safe_extraction_preserves_files_in_subdirectories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "valid.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("bundle/sample.png", b"png-bytes")
                archive.writestr("bundle/README.txt", b"source notes")
            destination = root / "out"
            extracted = safe_extract_zip(archive_path, destination)
            self.assertEqual(extracted, ["bundle/README.txt", "bundle/sample.png"])
            self.assertEqual((destination / "bundle" / "sample.png").read_bytes(), b"png-bytes")

    def test_path_traversal_is_rejected_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("safe/readme.txt", b"safe")
                archive.writestr("../escape.txt", b"no")
            destination = root / "out"
            with zipfile.ZipFile(archive_path) as archive:
                with self.assertRaisesRegex(ValueError, "Unsafe archive path"):
                    _validated_members(archive)
            self.assertFalse((root / "escape.txt").exists())
            self.assertFalse(destination.exists())

    def test_symbolic_links_and_duplicate_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            symlink_zip = root / "symlink.zip"
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (0o120777 << 16)
            with zipfile.ZipFile(symlink_zip, "w") as archive:
                archive.writestr(info, "target")
            with zipfile.ZipFile(symlink_zip) as archive:
                with self.assertRaisesRegex(ValueError, "Symbolic links"):
                    _validated_members(archive)

            duplicate_zip = root / "duplicate.zip"
            with zipfile.ZipFile(duplicate_zip, "w") as archive:
                archive.writestr("A.txt", b"a")
                archive.writestr("a.txt", b"b")
            with zipfile.ZipFile(duplicate_zip) as archive:
                with self.assertRaisesRegex(ValueError, "Duplicate archive path"):
                    _validated_members(archive)


if __name__ == "__main__":
    unittest.main()
