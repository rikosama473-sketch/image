from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
import generate_diffusion as engine  # noqa: E402


class DiffusionEngineContractTests(unittest.TestCase):
    def parse(self, *args: str):
        parser = engine.build_parser()
        parsed = parser.parse_args(["--model", "local-model", "--prompt", "anime portrait", *args])
        return parser, parsed

    def test_defaults_are_local_and_memory_conscious(self) -> None:
        _, args = self.parse()
        self.assertTrue(args.low_memory)
        self.assertFalse(args.allow_download)
        self.assertEqual(args.count, 1)
        self.assertEqual(args.device, "auto")
        self.assertEqual(args.precision, "auto")

    def test_resolution_must_be_a_multiple_of_eight(self) -> None:
        parser, args = self.parse("--width", "513")
        with self.assertRaises(SystemExit):
            engine.validate_args(args, parser)

    def test_batch_limit_prevents_large_parallel_generation(self) -> None:
        parser, args = self.parse("--count", "17")
        with self.assertRaises(SystemExit):
            engine.validate_args(args, parser)

    def test_local_lora_file_becomes_parent_plus_weight_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "style.safetensors"
            path.write_bytes(b"test-placeholder")
            source, weight_name = engine.resolve_lora_source(str(path), None)
            self.assertEqual(source, str(Path(directory).resolve()))
            self.assertEqual(weight_name, "style.safetensors")

    def test_prompt_and_model_are_required(self) -> None:
        parser = engine.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])


if __name__ == "__main__":
    unittest.main()
