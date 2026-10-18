from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, PngImagePlugin

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import extract_generation_metadata as extractor  # noqa: E402


class GenerationMetadataTests(unittest.TestCase):
    def test_a1111_parameter_block_extracts_prompt_model_and_lora(self) -> None:
        block = (
            "anime girl, silver hair\n"
            "Negative prompt: blurry, low quality\n"
            "Steps: 24, Sampler: Euler a, CFG scale: 6.5, Seed: 1234, "
            "Model: anime-base, Model hash: abcd1234"
        )
        values = extractor.parse_parameters(block)
        self.assertEqual(values["prompt"], "anime girl, silver hair")
        self.assertEqual(values["negative_prompt"], "blurry, low quality")
        self.assertEqual(values["base_model_identifier"], "anime-base")
        self.assertEqual(values["base_model_hash"], "abcd1234")
        self.assertEqual(values["steps"], "24")
        self.assertEqual(values["sampler"], "Euler a")
        self.assertEqual(values["cfg_scale"], "6.5")
        self.assertEqual(values["seed"], "1234")
        lora = extractor.parse_parameters("portrait <lora:my-style:0.8>")
        self.assertEqual(lora["lora_identifiers"], "my-style@0.8")
        self.assertEqual(lora["lora_weights_or_settings"], "my-style=0.8")

    def test_embedded_metadata_is_exported_without_changing_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "from-PixAI-123-0.png"
            info = PngImagePlugin.PngInfo()
            info.add_text("prompt", "anime character, blue hair")
            info.add_text("negative_prompt", "blur")
            info.add_text("Model", "compatible-base")
            info.add_text(
                "parameters",
                "anime character <lora:styleA:0.75>\n"
                "Steps: 20, Sampler: Euler, CFG scale: 5, Seed: 42",
            )
            Image.new("RGB", (24, 32), (20, 40, 60)).save(image_path, pnginfo=info)
            before = image_path.read_bytes()

            row = extractor.extract_one(image_path, root)

            self.assertEqual(row["prompt"], "anime character, blue hair")
            self.assertEqual(row["negative_prompt"], "blur")
            self.assertEqual(row["base_model_identifier"], "compatible-base")
            self.assertIn("styleA", row["lora_identifiers"])
            self.assertIn("styleA=0.75", row["lora_weights_or_settings"])
            self.assertEqual(row["steps"], "20")
            self.assertEqual(row["seed"], "42")
            self.assertEqual(row["metadata_present"], "true")
            self.assertEqual(image_path.read_bytes(), before)

    def test_no_metadata_is_unknown_not_guessed_from_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "from-PixAI-2034984086876227343-0.png"
            Image.new("RGB", (8, 8), (255, 255, 255)).save(image_path)
            row = extractor.extract_one(image_path, root)
            self.assertEqual(row["metadata_present"], "false")
            self.assertEqual(row["base_model_identifier"], "")
            self.assertEqual(row["lora_identifiers"], "")
            self.assertIn("No embedded", row["parse_notes"])

    def test_json_workflow_fields_can_be_flattened(self) -> None:
        flat = extractor.flatten_metadata({
            "workflow": '{"nodes":[{"type":"LoraLoader","inputs":{"lora_name":"style.safetensors","strength_model":0.7}}]}'
        })
        self.assertTrue(any("lora_name" in key and "style.safetensors" in value for key, value in flat))
        self.assertTrue(any("strength_model" in key and value == "0.7" for key, value in flat))

    def test_scan_skips_its_own_output_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data" / "cache").mkdir(parents=True)
            Image.new("RGB", (5, 6), (0, 0, 0)).save(root / "1.png")
            Image.new("RGB", (5, 6), (0, 0, 0)).save(root / "data" / "cache" / "report.png")
            self.assertEqual([p.relative_to(root).as_posix() for p in extractor.scan_images(root)], ["1.png"])


if __name__ == "__main__":
    unittest.main()
