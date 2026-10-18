from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
