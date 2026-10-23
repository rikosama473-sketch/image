from __future__ import annotations

import json
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



class DiffusionBatchTests(unittest.TestCase):
    class FakeTorch:
        class Generator:
            def __init__(self, device: str):
                self.device = device
            def manual_seed(self, seed: int):
                self.seed = seed
                return self

    class FakeImage:
        def __init__(self, seed: int):
            self.seed = seed
        def save(self, destination: Path) -> None:
            destination.write_bytes(("fixture-image-seed-" + str(self.seed)).encode("utf-8"))

    class FakePipeline:
        scheduler = None
        def __init__(self, failed_seeds=()):
            self.failed_seeds = set(failed_seeds)
            self.calls = []
        def __call__(self, **kwargs):
            seed = kwargs["generator"].seed
            self.calls.append(kwargs)
            if seed in self.failed_seeds:
                raise RuntimeError("fixture generation failure")
            return type("Result", (), {"images": [DiffusionBatchTests.FakeImage(seed)]})()

    def make_args(self, count=2, seed=40):
        parser = engine.build_parser()
        return parser.parse_args(["--model", "fixture-model", "--prompt", "anime test", "--count", str(count), "--seed", str(seed), "--width", "64", "--height", "64"])

    def test_successful_batch_saves_metadata_and_manifest(self):
        with tempfile.TemporaryDirectory() as tempdir:
            run_dir = Path(tempdir) / "run-success"
            args = self.make_args()
            result = engine.run_generation_batch(args, self.FakePipeline(), self.FakeTorch, "cpu", run_dir, "diffusers-test", "torch-test")
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(result["manifest"]["run_status"], "completed")
            self.assertEqual(result["manifest"]["generated_count"], 2)
            manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([item["seed"] for item in manifest["generated"]], [40, 41])
            for item in manifest["generated"]:
                image_path = run_dir / item["image_path"]
                self.assertTrue(image_path.is_file())
                self.assertEqual(json.loads(image_path.with_suffix(".json").read_text(encoding="utf-8"))["seed"], item["seed"])

    def test_partial_batch_preserves_success_and_records_failed_seed(self):
        with tempfile.TemporaryDirectory() as tempdir:
            run_dir = Path(tempdir) / "run-partial"
            args = self.make_args(count=3, seed=50)
            result = engine.run_generation_batch(args, self.FakePipeline(failed_seeds={51}), self.FakeTorch, "cpu", run_dir)
            self.assertEqual(result["exit_code"], 3)
            self.assertEqual(result["manifest"]["run_status"], "partial")
            self.assertEqual(result["manifest"]["generated_count"], 2)
            self.assertEqual(result["manifest"]["failed_count"], 1)
            self.assertEqual(result["manifest"]["failures"][0]["seed"], 51)
            self.assertTrue((run_dir / "image-001-seed-50.png").is_file())
            self.assertTrue((run_dir / "image-003-seed-52.png").is_file())

    def test_total_batch_failure_has_nonzero_exit_and_manifest(self):
        with tempfile.TemporaryDirectory() as tempdir:
            run_dir = Path(tempdir) / "run-failed"
            args = self.make_args(count=2, seed=60)
            result = engine.run_generation_batch(args, self.FakePipeline(failed_seeds={60, 61}), self.FakeTorch, "cpu", run_dir)
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(result["manifest"]["run_status"], "failed")
            self.assertEqual(result["manifest"]["generated_count"], 0)
            self.assertEqual(result["manifest"]["failed_count"], 2)
            self.assertTrue((run_dir / "run-manifest.json").is_file())

    def test_empty_pipeline_result_is_counted_as_failure(self):
        class EmptyPipeline:
            scheduler = None
            def __call__(self, **kwargs):
                return type("Result", (), {"images": []})()
        with tempfile.TemporaryDirectory() as tempdir:
            args = self.make_args(count=1, seed=70)
            result = engine.run_generation_batch(args, EmptyPipeline(), self.FakeTorch, "cpu", Path(tempdir) / "run-empty")
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(result["manifest"]["run_status"], "failed")
            self.assertIn("no devolvió ninguna imagen", result["manifest"]["failures"][0]["error"])


if __name__ == "__main__":
    unittest.main()
