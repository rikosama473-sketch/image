"""Regression tests for IMAGE's local diffusion job server."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
import local_server as server  # noqa: E402


class LocalGeneratorJobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_output_root = server.OUTPUT_ROOT
        self.output_root = Path(self.tempdir.name) / "outputs"
        server.OUTPUT_ROOT = self.output_root
        self.original_jobs = dict(server.JOBS)
        server.JOBS.clear()
        self.job_id = "a" * 32
        self.job_dir = self.output_root / ("ui-run-" + self.job_id)
        self.config = {
            "model": "model-fixture",
            "lora": "",
            "lora_weight_name": "",
            "prompt": "anime portrait",
            "negative_prompt": "",
            "width": 512,
            "height": 512,
            "steps": 4,
            "guidance_scale": 7.0,
            "seed": 7,
            "count": 1,
            "lora_scale": 0.8,
            "device": "cpu",
            "precision": "fp32",
            "allow_download": False,
            "cpu_offload": False,
            "low_memory": True,
        }
        server.JOBS[self.job_id] = {"id": self.job_id, "status": "queued", "config": self.config}

    def tearDown(self) -> None:
        server.JOBS.clear()
        server.JOBS.update(self.original_jobs)
        server.OUTPUT_ROOT = self.original_output_root
        self.tempdir.cleanup()

    def run_fake_engine(self, outputs: int, requested: int, return_code: int = 0):
        self.config["count"] = requested

        def fake_run(command, **kwargs):
            # Mirror generate_diffusion.py: output is nested under a run-<stamp> folder.
            run_dir = self.job_dir / "run-fixture-seed-7"
            if outputs:
                run_dir.mkdir(parents=True, exist_ok=True)
                for index in range(outputs):
                    (run_dir / f"image-{index + 1:03d}-seed-{7 + index}.png").write_bytes(b"PNG-fixture")
            return subprocess.CompletedProcess(
                args=command,
                returncode=return_code,
                stdout=f"Saved {outputs} test images",
                stderr="engine warning" if return_code else "",
            )

        with mock.patch.object(server.subprocess, "run", side_effect=fake_run):
            server._run_job(self.job_id, self.config, self.job_dir)
        return server.JOBS[self.job_id]

    def test_discovers_images_inside_nested_run_directory(self) -> None:
        job = self.run_fake_engine(outputs=1, requested=1)
        self.assertEqual(job["status"], "completed")
        self.assertEqual(len(job["images"]), 1)
        self.assertEqual(
            job["images"][0],
            f"/generated/ui-run-{self.job_id}/run-fixture-seed-7/image-001-seed-7.png",
        )

    def test_partial_generation_preserves_outputs_and_reports_missing_count(self) -> None:
        job = self.run_fake_engine(outputs=1, requested=3)
        self.assertEqual(job["status"], "partial")
        self.assertEqual(job["requested_count"], 3)
        self.assertEqual(len(job["images"]), 1)
        self.assertIn("1 de 3", job["error"])

    def test_engine_failure_with_saved_outputs_is_reported_as_partial(self) -> None:
        job = self.run_fake_engine(outputs=1, requested=2, return_code=1)
        self.assertEqual(job["status"], "partial")
        self.assertEqual(len(job["images"]), 1)

    def test_no_output_is_a_clear_failure(self) -> None:
        job = self.run_fake_engine(outputs=0, requested=1, return_code=0)
        self.assertEqual(job["status"], "failed")
        self.assertEqual(job["images"], [])
        self.assertTrue(job["error"])


class LocalGeneratorPayloadTests(unittest.TestCase):
    def test_payload_rejects_invalid_resolution_and_boolean_as_integer(self) -> None:
        with self.assertRaisesRegex(ValueError, "múltiplos de ocho"):
            server._validate_payload({"model": "m", "prompt": "x", "width": 513})
        with self.assertRaisesRegex(ValueError, "count debe ser un número entero"):
            server._validate_payload({"model": "m", "prompt": "x", "count": True})

    def test_payload_defaults_to_local_only_and_low_memory_mode(self) -> None:
        parsed = server._validate_payload({"model": "m", "prompt": "anime portrait"})
        self.assertFalse(parsed["allow_download"])
        self.assertTrue(parsed["low_memory"])
        self.assertEqual(parsed["device"], "auto")
        self.assertEqual(parsed["count"], 1)


if __name__ == "__main__":
    unittest.main()
