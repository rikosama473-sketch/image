import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

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


    def test_base_cutout_manifest_and_registry_are_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "original.png"
            Image.new("RGBA", (8, 8), (80, 110, 150, 255)).save(source)
            (root / "data").mkdir()
            (root / "data" / "character-prompt-registry.json").write_text(
                json.dumps({"characters": [{"id": "pibara", "source_images": []}]}),
                encoding="utf-8",
            )

            original_make_cutout = MODULE.make_cutout

            def fake_make_cutout(source_path, target_path, session):
                with Image.open(source_path) as opened:
                    rgba = opened.convert("RGBA")
                alpha = Image.new("L", rgba.size, 255)
                alpha.putpixel((0, 0), 0)
                rgba.putalpha(alpha)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                rgba.save(target_path, format="PNG")
                return {
                    "file": str(target_path),
                    "sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
                    "dimensions": list(rgba.size),
                    "transparent_pixel_ratio": 1 / 64,
                    "opaque_pixel_ratio": 63 / 64,
                    "quality_warning": None,
                }

            MODULE.make_cutout = fake_make_cutout
            try:
                result = MODULE.ensure_base_character_cutout(
                    root,
                    "pibara",
                    source,
                    "from-PixAI-reference.png",
                    "https://raw.githubusercontent.com/owner/repo/main/from-PixAI-reference.png",
                    "0123456789abcdef",
                    (8, 8),
                    object(),
                )
            finally:
                MODULE.make_cutout = original_make_cutout

            manifest_path = root / result["assets"]["alpha_mask"]["file"].replace(
                "-alpha-mask.png", "-base-manifest.json"
            )
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["sha256"], "0123456789abcdef")
            self.assertFalse(manifest["is_ai_generated"])
            self.assertEqual(manifest["asset_kind"], "whole_character_foreground_cutout")
            self.assertTrue((root / manifest["assets"]["alpha_mask"]["file"]).is_file())
            registry = json.loads(
                (root / "data" / "character-prompt-registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry["characters"][0]["base_assets"][0]["status"], "derived_not_ai_generated")

    def test_confirmed_pibara_reference_cannot_be_reused_for_other_characters(self):
        reference = "from-PixAI-2034984086876227343-0.png"
        self.assertEqual(MODULE.validate_character_reference("pibara", reference), reference)
        for character_id in ("sunna", "chie"):
            with self.subTest(character_id=character_id):
                with self.assertRaises(SystemExit):
                    MODULE.validate_character_reference(character_id, reference)

    def test_source_url_escapes_spaces(self):
        self.assertEqual(
            MODULE.source_url("owner/repo", "main", "folder/my character.png"),
            "https://raw.githubusercontent.com/owner/repo/main/folder/my%20character.png",
        )


if __name__ == "__main__":
    unittest.main()
