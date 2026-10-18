from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import train_lora  # noqa: E402
import summarize_generation_metadata  # noqa: E402


class MetadataSummaryTests(unittest.TestCase):
    def test_summary_reports_coverage_but_never_copies_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "metadata.csv"
            output = Path(directory) / "summary.json"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "path", "format", "metadata_present", "prompt", "negative_prompt",
                        "base_model_identifier", "base_model_hash", "lora_identifiers",
                        "lora_weights_or_settings", "sampler", "steps", "cfg_scale", "seed",
                    ],
                )
                writer.writeheader()
                writer.writerow({
                    "path": "a.png",
                    "format": "PNG",
                    "metadata_present": "true",
                    "prompt": "PRIVATE_POSITIVE_PROMPT",
                    "negative_prompt": "PRIVATE_NEGATIVE_PROMPT",
                    "base_model_identifier": "local-model-a",
                    "base_model_hash": "hash-a",
                    "lora_identifiers": "style-a@0.8",
                    "lora_weights_or_settings": "style-a=0.8",
                    "sampler": "Euler",
                    "steps": "20",
                    "cfg_scale": "6.5",
                    "seed": "123",
                })
                writer.writerow({
                    "path": "b.png",
                    "format": "PNG",
                    "metadata_present": "false",
                    "prompt": "",
                    "negative_prompt": "",
                    "base_model_identifier": "",
                    "base_model_hash": "",
                    "lora_identifiers": "",
                    "lora_weights_or_settings": "",
                    "sampler": "",
                    "steps": "",
                    "cfg_scale": "",
                    "seed": "",
                })

            report = summarize_generation_metadata.summarize(source)
            output.write_text(json.dumps(report), encoding="utf-8")
            serialized = output.read_text(encoding="utf-8")
            self.assertEqual(report["image_count"], 2)
            self.assertEqual(report["field_coverage"]["prompt"]["present"], 1)
            self.assertEqual(report["field_coverage"]["base_model_identifier"]["present"], 1)
            self.assertEqual(report["observed_base_model_identifiers"][0]["identifier"], "local-model-a")
            self.assertEqual(report["model_family_decision"], "pending_manual_review")
            self.assertNotIn("PRIVATE_POSITIVE_PROMPT", serialized)
            self.assertNotIn("PRIVATE_NEGATIVE_PROMPT", serialized)

    def test_empty_metadata_csv_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "empty.csv"
            source.write_text("path,metadata_present\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                summarize_generation_metadata.summarize(source)


class LoRATrainingGuardTests(unittest.TestCase):
    def test_git_blob_sha_matches_known_empty_git_blob(self) -> None:
        self.assertEqual(
            train_lora.git_blob_sha(b""),
            "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
        )

    def test_model_family_is_read_from_model_index_not_directory_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="this-name-does-not-imply-sdxl-") as directory:
            model = Path(directory)
            (model / "model_index.json").write_text(
                json.dumps({"_class_name": "StableDiffusionPipeline"}),
                encoding="utf-8",
            )
            family, resolved, is_local = train_lora.detect_model_family(str(model), "auto", False)
            self.assertEqual(family, "sd")
            self.assertEqual(resolved, str(model.resolve()))
            self.assertTrue(is_local)
            with self.assertRaises(ValueError):
                train_lora.detect_model_family(str(model), "sdxl", False)

    def test_remote_model_requires_explicit_family(self) -> None:
        with self.assertRaises(ValueError):
            train_lora.detect_model_family("org/a-model", "auto", False)
        family, model, is_local = train_lora.detect_model_family("org/a-model", "sdxl", False)
        self.assertEqual(family, "sdxl")
        self.assertEqual(model, "org/a-model")
        self.assertFalse(is_local)

    def test_unknown_and_mixed_source_checkpoints_require_explicit_review(self) -> None:
        examples = [
            {"path": "a.png", "source_model": "model-a"},
            {"path": "b.png", "source_model": ""},
        ]
        with self.assertRaises(ValueError):
            train_lora.verify_source_models(examples, False, False)
        observed, unknown = train_lora.verify_source_models(examples, True, False)
        self.assertEqual(observed["model-a"], 1)
        self.assertEqual(unknown, 1)
        examples[1]["source_model"] = "model-b"
        with self.assertRaises(ValueError):
            train_lora.verify_source_models(examples, False, False)
        observed, unknown = train_lora.verify_source_models(examples, False, True)
        self.assertEqual(len(observed), 2)
        self.assertEqual(unknown, 0)

    def test_training_dataset_uses_approved_images_and_keeps_original_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows_path = root / "labels.csv"
            captions_path = root / "captions.csv"
            fields = [
                "path", "visual_review", "license_review", "training_permission",
                "base_model_identifier",
            ]
            rows = []
            captions = []
            original_bytes = {}
            for index in range(9):
                relative = f"reference-{index:02d}.png"
                path = root / relative
                Image.new("RGB", (24, 32), (index, 40, 90)).save(path)
                original_bytes[relative] = path.read_bytes()
                rows.append({
                    "path": relative,
                    "visual_review": "approved",
                    "license_review": "approved",
                    "training_permission": "approved",
                    "base_model_identifier": "model-a",
                })
                captions.append({"path": relative, "caption": f"reviewed caption {index}"})
            rows.append({
                "path": "not-approved.png",
                "visual_review": "unreviewed",
                "license_review": "unreviewed",
                "training_permission": "unreviewed",
                "base_model_identifier": "",
            })
            Image.new("RGB", (24, 32), (0, 0, 0)).save(root / "not-approved.png")
            with rows_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with captions_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["path", "caption"])
                writer.writeheader()
                writer.writerows(captions)

            examples, skipped, _ = train_lora.load_approved_examples(
                rows_path, root, captions_path, None
            )
            models, unknown = train_lora.verify_source_models(examples, False, False)
            self.assertEqual(len(examples), 9)
            self.assertEqual(skipped["not_fully_approved"], 1)
            self.assertEqual(models["model-a"], 9)
            self.assertEqual(unknown, 0)

            train_dir, validation_dir, train_rows, validation_rows = train_lora.prepare_imagefolder(
                examples, root / "staged-dataset", seed=42, validation_ratio=0.1
            )
            self.assertEqual(len(train_rows), 8)
            self.assertEqual(len(validation_rows), 1)
            self.assertEqual(len((train_dir / "metadata.jsonl").read_text(encoding="utf-8").splitlines()), 8)
            self.assertEqual(len((validation_dir / "metadata.jsonl").read_text(encoding="utf-8").splitlines()), 1)
            train_record = json.loads((train_dir / "metadata.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("file_name", train_record)
            self.assertTrue(train_record["text"].startswith("reviewed caption "))
            for relative, before in original_bytes.items():
                self.assertEqual((root / relative).read_bytes(), before)

    def test_missing_caption_blocks_approved_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "approved.png"
            Image.new("RGB", (8, 8), (10, 20, 30)).save(image_path)
            labels_path = root / "labels.csv"
            with labels_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["path", "visual_review", "license_review", "training_permission"],
                )
                writer.writeheader()
                writer.writerow({
                    "path": image_path.name,
                    "visual_review": "approved",
                    "license_review": "approved",
                    "training_permission": "approved",
                })
            with self.assertRaisesRegex(ValueError, "no caption"):
                train_lora.load_approved_examples(labels_path, root, None, None)

    def test_caption_template_does_not_mark_permissions_approved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labels_path = root / "labels.csv"
            with labels_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["path", "visual_review", "license_review", "training_permission"],
                )
                writer.writeheader()
                writer.writerow({
                    "path": "image.png",
                    "visual_review": "unreviewed",
                    "license_review": "unreviewed",
                    "training_permission": "unreviewed",
                })
            output = root / "captions.csv"
            count = train_lora.make_caption_template(labels_path, output, root)
            self.assertEqual(count, 1)
            with output.open("r", encoding="utf-8", newline="") as handle:
                template = list(csv.DictReader(handle))
            self.assertEqual(template, [{"path": "image.png", "caption": ""}])


if __name__ == "__main__":
    unittest.main()
