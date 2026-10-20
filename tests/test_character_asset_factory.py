import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock

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
            "anatomy-guide-1": 1,
            "anatomy-front-v2-1": 1,
            "anatomy-side-1": 1,
            "anatomy-back-1": 1,
            "anatomy-joint-guide-1": 1,
            "anatomy-sheet-4": 4,
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

    def test_anatomy_pack_uses_full_body_reconstruction_prompt(self):
        self.assertEqual(len(MODULE.PACKS["anatomy-guide-1"]), 1)
        slug, instruction = MODULE.PACKS["anatomy-guide-1"][0]
        self.assertEqual(slug, "full-body-anatomy-a-pose")
        self.assertIn("full-body", instruction)
        self.assertIn("ANATOMY_BASE", MODULE.__dict__)
        self.assertIn("do not preserve the input crop", MODULE.ANATOMY_BASE)
        self.assertIn("hands, fingers and both feet visible", MODULE.ANATOMY_BASE)
        self.assertIn("later manual component separation", MODULE.ANATOMY_BASE)
        self.assertIn("exact hairstyle and silhouette", MODULE.ANATOMY_BASE)
        self.assertIn("Do not redesign the hairstyle", MODULE.ANATOMY_BASE)

    def test_multiple_anatomy_views_have_specific_instructions(self):
        self.assertIn("orientation and pose specified", MODULE.ANATOMY_BASE)
        cases = {
            "anatomy-front-v2-1": ("full-body-front-a-pose-v2", "Front-view full-body"),
            "anatomy-side-1": ("full-body-side-profile", "strict 90-degree side profile"),
            "anatomy-back-1": ("full-body-back-view", "directly behind"),
            "anatomy-joint-guide-1": ("full-body-joint-guide", "construction marks"),
        }
        for pack, (slug, phrase) in cases.items():
            with self.subTest(pack=pack):
                self.assertEqual(len(MODULE.PACKS[pack]), 1)
                self.assertEqual(MODULE.PACKS[pack][0][0], slug)
                self.assertIn(phrase.lower(), MODULE.PACKS[pack][0][1].lower())
                self.assertIn("exact hairstyle and silhouette", MODULE.ANATOMY_BASE)

    def test_anatomy_sheet_batch_contains_four_distinct_views(self):
        expected = {
            "batch-front-a-pose",
            "batch-side-profile",
            "batch-back-view",
            "batch-joint-guide",
        }
        actual = {slug for slug, _ in MODULE.PACKS["anatomy-sheet-4"]}
        self.assertEqual(actual, expected)
        self.assertIn("exact hairstyle and silhouette", MODULE.ANATOMY_BASE)
        self.assertIn("orientation and pose specified", MODULE.ANATOMY_BASE)
        for slug, prompt in MODULE.PACKS["anatomy-sheet-4"]:
            with self.subTest(slug=slug):
                self.assertTrue(prompt.strip())
                self.assertIn("plain light background", prompt.lower())

    def test_optional_huggingface_token_is_not_logged_or_passed_when_absent(self):
        client_class = Mock(return_value=object())
        out = io.StringIO()
        with redirect_stdout(out):
            MODULE.build_space_client(client_class, " hf_test_secret_value ")
        client_class.assert_called_once_with(MODULE.SPACE_ID, hf_token="hf_test_secret_value", verbose=True)
        self.assertNotIn("hf_test_secret_value", out.getvalue())

        client_class.reset_mock()
        out = io.StringIO()
        with redirect_stdout(out):
            MODULE.build_space_client(client_class, "")
        client_class.assert_called_once_with(MODULE.SPACE_ID, verbose=True)
        self.assertNotIn("hf_test_secret_value", out.getvalue())

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
