from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from publish_character_layers import collect_publish_files, safe_slug, safe_target_prefix  # noqa: E402


class PublishCharacterLayersTests(unittest.TestCase):
    def test_safe_character_prefix(self) -> None:
        self.assertEqual(safe_target_prefix("generated/character-layers/{character_id}", "Pibra"), "generated/character-layers/pibra")
        with self.assertRaises(ValueError):
            safe_target_prefix("../escape/{character_id}", "pibra")

    def test_collect_only_safe_supported_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "hair").mkdir()
            (root / "hair" / "bob.png").write_bytes(b"not empty test bytes")
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            self.assertEqual([relative for _, relative in collect_publish_files(root)], ["hair/bob.png", "manifest.json"])
            (root / "secret.env").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsupported asset file type"):
                collect_publish_files(root)

    def test_character_slug_rejects_empty_value(self) -> None:
        self.assertEqual(safe_slug("PIBARA"), "pibara")
        with self.assertRaises(ValueError):
            safe_slug("../")


if __name__ == "__main__":
    unittest.main()
