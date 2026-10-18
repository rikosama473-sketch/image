from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
import local_server  # noqa: E402


class LocalServerTests(unittest.TestCase):
    def valid_payload(self):
        return {
            "model": "models/base",
            "lora": "models/style.safetensors",
            "prompt": "anime portrait",
        }

    def test_validation_defaults_to_no_remote_download_and_single_image(self) -> None:
        config = local_server._validate_payload(self.valid_payload())
        self.assertFalse(config["allow_download"])
        self.assertEqual(config["count"], 1)
        self.assertTrue(config["low_memory"])
        self.assertEqual(config["device"], "auto")

    def test_prompt_and_model_are_required(self) -> None:
        for payload in (
            {"model": "models/base", "prompt": "  "},
            {"model": "", "prompt": "portrait"},
        ):
            with self.assertRaises(ValueError):
                local_server._validate_payload(payload)

    def test_resolution_and_count_are_bounded(self) -> None:
        for extra in ({"width": 513}, {"height": 9999}, {"count": 9}, {"steps": 0}):
            payload = self.valid_payload()
            payload.update(extra)
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                local_server._validate_payload(payload)

    def test_remote_download_is_an_explicit_flag(self) -> None:
        config = local_server._validate_payload(self.valid_payload())
        command = local_server._build_command(config, PROJECT_ROOT / "outputs/generated/test")
        self.assertNotIn("--allow-download", command)
        config["allow_download"] = True
        command = local_server._build_command(config, PROJECT_ROOT / "outputs/generated/test")
        self.assertIn("--allow-download", command)

    def test_arguments_are_passed_without_shell_interpretation(self) -> None:
        payload = self.valid_payload()
        payload["prompt"] = 'portrait; echo "should-not-run"'
        config = local_server._validate_payload(payload)
        command = local_server._build_command(config, PROJECT_ROOT / "outputs/generated/test")
        self.assertIn('portrait; echo "should-not-run"', command)
        self.assertNotIn("shell", command)

    def test_output_path_guard_blocks_traversal(self) -> None:
        self.assertIsNone(local_server._safe_output_path("../README.md"))
        allowed = local_server._safe_output_path("session/image.png")
        self.assertIsNotNone(allowed)
        self.assertEqual(allowed.suffix, ".png")

    def test_local_assets_lists_only_supported_model_families_and_loras(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sd = root / "models" / "bases" / "sd"
            sdxl = root / "models" / "bases" / "sdxl"
            unsupported = root / "models" / "bases" / "other"
            for model, class_name in (
                (sd, "StableDiffusionPipeline"),
                (sdxl, "StableDiffusionXLPipeline"),
                (unsupported, "FluxPipeline"),
            ):
                model.mkdir(parents=True)
                (model / "model_index.json").write_text(
                    json.dumps({"_class_name": class_name}), encoding="utf-8"
                )
                (model / "diffusion_pytorch_model.safetensors").write_bytes(b"base weights should not be listed as a LoRA")

            lora_dir = root / "models" / "loras"
            lora_dir.mkdir(parents=True)
            (lora_dir / "custom-style.safetensors").write_bytes(b"lora")
            (lora_dir / "notes.txt").write_text("not a model", encoding="utf-8")

            trained = root / "outputs" / "training-lora" / "run-1"
            trained.mkdir(parents=True)
            artifact = trained / "pytorch_lora_weights.safetensors"
            artifact.write_bytes(b"trained lora")
            (trained / "training-result.json").write_text(
                json.dumps({"status": "completed", "artifact": str(artifact)}), encoding="utf-8"
            )
            failed = root / "outputs" / "training-lora" / "run-failed"
            failed.mkdir(parents=True)
            (failed / "pytorch_lora_weights.safetensors").write_bytes(b"partial artifact")
            (failed / "training-result.json").write_text(
                json.dumps({"status": "failed"}), encoding="utf-8"
            )

            assets = local_server._list_local_assets(root)
            self.assertEqual(
                {item["path"] for item in assets["models"]},
                {"models/bases/sd", "models/bases/sdxl"},
            )
            families = {item["path"]: item["family"] for item in assets["models"]}
            self.assertEqual(families["models/bases/sd"], "sd")
            self.assertEqual(families["models/bases/sdxl"], "sdxl")
            self.assertEqual(
                {item["path"] for item in assets["loras"]},
                {
                    "models/loras/custom-style.safetensors",
                    "outputs/training-lora/run-1/pytorch_lora_weights.safetensors",
                },
            )

    def test_local_assets_ignore_malformed_model_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = root / "models" / "broken"
            model.mkdir(parents=True)
            (model / "model_index.json").write_text("{not json", encoding="utf-8")
            assets = local_server._list_local_assets(root)
            self.assertEqual(assets, {"models": [], "loras": []})


if __name__ == "__main__":
    unittest.main()
