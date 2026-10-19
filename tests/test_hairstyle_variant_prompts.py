import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from scripts.generate_hairstyle_variants import BASE_INSTRUCTIONS, STYLE_PACKS, extract_embedded_prompt, prepare_head_reference

ROOT = Path(__file__).resolve().parents[1]


class HairstyleVariantPromptTests(unittest.TestCase):
    def test_every_style_pack_contains_six_distinct_variants(self):
        for pack_name, variants in STYLE_PACKS.items():
            with self.subTest(pack=pack_name):
                self.assertEqual(len(variants), 6)
                self.assertEqual(len({slug for slug, _ in variants}), 6)

    def test_prompts_prioritize_hair_and_preserve_identity(self):
        prompt = BASE_INSTRUCTIONS.lower()
        for required_phrase in ("change only the hairstyle", "preserve the face", "hair color", "no nudity", "dominant variable"):
            with self.subTest(phrase=required_phrase):
                self.assertIn(required_phrase, prompt)

    def test_head_crop_excludes_the_full_original_and_creates_a_square_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.png"
            crop = root / "reference-head-crop.png"
            Image.new("RGB", (600, 1200), "white").save(source)
            data_url, metadata = prepare_head_reference(source, crop)
            self.assertTrue(data_url.startswith("data:image/png;base64,"))
            self.assertTrue(crop.is_file())
            with Image.open(crop) as output:
                self.assertEqual(output.size, (1024, 1024))
            self.assertEqual(metadata["crop_box_pixels"], [12, 0, 588, 240])
            self.assertEqual(metadata["api_input_dimensions"], [1024, 1024])

    def test_original_prompt_is_recovered_when_embedded_metadata_exists(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as temp:
            source = Path(temp) / "source-with-prompt.png"
            metadata = PngInfo()
            metadata.add_text("prompt", "sample prompt preserved exactly")
            Image.new("RGB", (600, 1200), "white").save(source, pnginfo=metadata)
            prompt, keys = extract_embedded_prompt(source, ROOT)
            self.assertEqual(prompt, "sample prompt preserved exactly")
            self.assertIn("prompt", [key.lower() for key in keys])

    def test_registry_has_five_slots_without_invented_canonical_prompts(self):
        registry = json.loads((ROOT / "data" / "character-prompt-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [item["id"] for item in registry["characters"]],
            ["pibara", "chie", "sunna", "personaje-4", "personaje-5"],
        )
        for item in registry["characters"]:
            with self.subTest(character=item["id"]):
                self.assertIsNone(item["canonical_prompt"])
                self.assertEqual(item["source_images"], [])
                self.assertEqual(item["source_prompt_examples"], [])


if __name__ == "__main__":
    unittest.main()
