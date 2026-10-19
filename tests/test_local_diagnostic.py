from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "local-diagnostic"))
import image_local_diagnostic as diagnostic  # noqa: E402


class LocalDiagnosticTests(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        info = PngInfo()
        info.add_text(
            "parameters",
            "PRIVATE_PROMPT_SENTINEL\nNegative prompt: PRIVATE_NEGATIVE_SENTINEL\n"
            "Steps: 12, Sampler: Euler a, CFG scale: 7, Seed: 42, Model hash: abc123",
        )
        info.add_text("workflow", json.dumps({"checkpoint": "sd15-local-test", "lora_name": "style-test"}))
        Image.new("RGB", (32, 48), (10, 20, 30)).save(root / "sample.png", pnginfo=info)
        Image.new("RGB", (64, 64), (30, 20, 10)).save(root / "plain.jpg")
        return root

    def test_scan_only_reads_metadata_and_never_exports_prompt_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_source(Path(directory) / "source")
            output = Path(directory) / "reports"
            zip_path = diagnostic.run_diagnostic(root, output)
            self.assertTrue(zip_path.is_file())
            with (output / "image_inventory.csv").open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            sample = next(row for row in rows if row["relative_path"] == "sample.png")
            self.assertEqual(sample["resolution"], "32x48")
            self.assertEqual(sample["prompt_present"], "true")
            self.assertEqual(sample["negative_prompt_present"], "true")
            self.assertEqual(sample["steps"], "12")
            self.assertEqual(sample["sampler"], "Euler a")
            self.assertEqual(sample["seed"], "42")
            self.assertNotEqual(sample["sha256"], "")
            with zipfile.ZipFile(zip_path) as bundle:
                all_text = "".join(
                    bundle.read(name).decode("utf-8", errors="replace")
                    for name in bundle.namelist()
                    if name.endswith((".json", ".csv", ".txt"))
                )
            self.assertNotIn("PRIVATE_PROMPT_SENTINEL", all_text)
            self.assertNotIn("PRIVATE_NEGATIVE_SENTINEL", all_text)
            self.assertIn("sd15-local-test", all_text)
            self.assertIn("IMAGE-Diagnostic-Bundle.zip.sha256", list(p.name for p in output.iterdir()))

    def test_original_image_bytes_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_source(Path(directory) / "source")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            diagnostic.run_diagnostic(root, Path(directory) / "reports")
            after = {p.name: p.read_bytes() for p in root.iterdir()}
            self.assertEqual(before, after)

    def test_reports_must_be_outside_source_folder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_source(Path(directory) / "source")
            with self.assertRaisesRegex(ValueError, "outside the selected source folder"):
                diagnostic.run_diagnostic(root, root / "reports")

    def test_scan_limits_bound_the_number_of_images(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            for index in range(5):
                Image.new("RGB", (8, 8), (index, 0, 0)).save(root / f"{index}.png")
            rows, summary = diagnostic.scan_images(root, max_files=3)
            self.assertEqual(len(rows), 3)
            self.assertTrue(summary["truncated_by_safety_limit"])
            self.assertEqual(summary["counts"]["images_skipped_after_file_limit"], 2)

    def test_model_inspection_is_metadata_only_and_does_not_open_weights(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "models"
            model = root / "base"
            model.mkdir(parents=True)
            (model / "model_index.json").write_text(
                json.dumps({"_class_name": "StableDiffusionPipeline"}), encoding="utf-8"
            )
            for component in ("unet", "vae", "scheduler", "tokenizer", "text_encoder"):
                (model / component).mkdir()
            lora_dir = root / "loras"
            lora_dir.mkdir()
            (lora_dir / "style.safetensors").write_bytes(b"not opened")
            report = diagnostic.scan_local_models(root)
            self.assertTrue(report["models_root_found"])
            self.assertEqual(report["model_candidates"][0]["family_hint"], "sd")
            self.assertEqual(report["model_candidates"][0]["status"], "directory_structure_only_not_load_tested")
            self.assertEqual(report["lora_file_names"], ["loras/style.safetensors"])
            self.assertTrue(report["weights_were_not_opened"])

    def test_self_test_path_is_present(self) -> None:
        self.assertIn("SELF-TEST PASSED", Path(diagnostic.__file__).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
