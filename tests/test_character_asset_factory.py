import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_character_assets_free.py"
SPEC = importlib.util.spec_from_file_location("character_asset_factory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CharacterAssetFactoryTests(unittest.TestCase):
    def test_pack_counts_and_slugs(self):
        expected = {
            "hair-core-5": 5,
            "expressions-core-5": 5,
            "eyes-4": 4,
            "accessories-4": 4,
            "face-details-4": 4,
        }
        self.assertEqual(set(MODULE.PACKS), set(expected))
        for name, count in expected.items():
            with self.subTest(pack=name):
                self.assertEqual(len(MODULE.PACKS[name]), count)
                slugs = [slug for slug, _ in MODULE.PACKS[name]]
                self.assertEqual(len(slugs), len(set(slugs)))

    def test_every_variant_has_one_change_instruction(self):
        self.assertIn("Preserve exact recognizable identity", MODULE.BASE)
        self.assertIn("Make only the single change requested below", MODULE.BASE)
        for variants in MODULE.PACKS.values():
            for slug, instruction in variants:
                self.assertTrue(slug.strip())
                self.assertTrue(instruction.strip())

    def test_reference_validation(self):
        self.assertEqual(MODULE.validate_path("ref/character.png"), "ref/character.png")
        for path in ("../outside.png", "/absolute.png", "image.svg", "ref/../outside.png"):
            with self.subTest(path=path):
                with self.assertRaises(SystemExit):
                    MODULE.validate_path(path)

    def test_source_url_escapes_spaces(self):
        self.assertEqual(
            MODULE.source_url("owner/repo", "main", "folder/my character.png"),
            "https://raw.githubusercontent.com/owner/repo/main/folder/my%20character.png",
        )


if __name__ == "__main__":
    unittest.main()
