"""Regression tests for IMAGE's local diffusion job server."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode
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


    def test_diagnostics_recognizes_a_diffusers_folder_without_loading_it(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            model_dir = Path(tempdir) / "fixture-model"
            model_dir.mkdir()
            (model_dir / "model_index.json").write_text(json.dumps({"_class_name": "TestPipeline"}), encoding="utf-8")
            with mock.patch.object(server.importlib.util, "find_spec", side_effect=lambda name: object() if name in {"torch", "diffusers", "safetensors"} else None):
                report = server._diagnose_environment(str(model_dir), device="cpu")
        self.assertTrue(report["dependencies_ready"])
        self.assertEqual(report["model"]["state"], "local_directory_ready")
        self.assertTrue(report["model"]["ready_to_try"])
        self.assertFalse(report["inference_started"])
        self.assertTrue(report["downloads_default_off"])

    def test_unknown_cached_model_is_not_reported_as_ready_without_downloads(self) -> None:
        report = server._diagnose_environment("org/example-model", allow_download=False)
        self.assertEqual(report["model"]["state"], "hub_identifier_or_cached_model")
        self.assertFalse(report["model"]["ready_to_try"])
        self.assertFalse(report["inference_started"])
        self.assertIn("no se descargará nada", report["model"]["message"])

    def test_downloading_weights_requires_the_explicit_download_flag(self) -> None:
        report = server._diagnose_environment("org/example-model", allow_download=True)
        self.assertEqual(report["model"]["state"], "hub_identifier_download_enabled")
        self.assertTrue(report["model"]["ready_to_try"])
        self.assertTrue(report["allow_download"])

    def test_preflight_interface_is_connected_to_local_endpoint(self) -> None:
        index = (PROJECT_ROOT / "tools/image-creator/index.html").read_text(encoding="utf-8")
        app = (PROJECT_ROOT / "tools/image-creator/app.js").read_text(encoding="utf-8")
        self.assertIn('id="diagnose-button"', index)
        self.assertIn('id="diagnostics-panel"', index)
        self.assertIn('"/api/diagnostics?"', app)
        self.assertIn("async function runDiagnostics()", app)



    def test_scan_local_models_only_returns_valid_diffusers_pipeline_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            valid = root / "models" / "sample-pipeline"
            valid.mkdir(parents=True)
            (valid / "model_index.json").write_text(json.dumps({"_class_name": "StableDiffusionPipeline"}), encoding="utf-8")
            malformed = root / "models" / "bad-model"
            malformed.mkdir()
            (malformed / "model_index.json").write_text("{not-json", encoding="utf-8")
            unsupported = root / "models" / "checkpoint-file"
            unsupported.mkdir()
            (unsupported / "model_index.json").write_text(json.dumps({"name": "not a pipeline"}), encoding="utf-8")
            with mock.patch.object(server, "_model_search_roots", return_value=[(root / "models", "project")]):
                report = server._scan_local_models()
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["models"][0]["pipeline_class"], "StableDiffusionPipeline")
        self.assertEqual(report["models"][0]["label"], "sample-pipeline")
        self.assertTrue(Path(report["models"][0]["path"]).is_absolute())
        self.assertFalse(report["downloads_performed"])
        self.assertFalse(report["weights_loaded"])

    def test_model_scanner_handles_missing_roots_without_throwing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            missing_root = Path(tempdir) / "does-not-exist"
            with mock.patch.object(server, "_model_search_roots", return_value=[(missing_root, "project")]):
                report = server._scan_local_models()
        self.assertEqual(report["models"], [])
        self.assertEqual(report["count"], 0)
        self.assertFalse(report["truncated"])

    def test_model_picker_interface_calls_read_only_inventory(self) -> None:
        index = (PROJECT_ROOT / "tools/image-creator/index.html").read_text(encoding="utf-8")
        app = (PROJECT_ROOT / "tools/image-creator/app.js").read_text(encoding="utf-8")
        self.assertIn('id="scan-models-button"', index)
        self.assertIn('id="local-model-picker"', index)
        self.assertIn('api("/api/models")', app)
        self.assertIn("async function scanLocalModels()", app)



class LocalGeneratorHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.CreatorHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def request(self, path: str):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request("GET", path)
        response = connection.getresponse()
        status = response.status
        body = response.read()
        headers = dict(response.getheaders())
        connection.close()
        return status, body, headers

    def test_serves_local_creator_ui_and_diagnostic_assets(self) -> None:
        status, body, headers = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b"IMAGE", body)
        self.assertIn("Content-Security-Policy", headers)

        status, body, _ = self.request("/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"runDiagnostics", body)

        status, body, _ = self.request("/app.css")
        self.assertEqual(status, 200)
        self.assertIn(b"diagnostics-panel", body)

    def test_model_inventory_endpoint_is_read_only_and_returns_local_paths(self) -> None:
        status, body, _ = self.request("/api/models")
        report = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertIn("models", report)
        self.assertFalse(report["downloads_performed"])
        self.assertFalse(report["weights_loaded"])

    def test_diagnostic_endpoint_reports_that_it_does_not_generate_or_download(self) -> None:
        query = urlencode({"model": "org/example-model", "device": "cpu", "allow_download": "false"})
        status, body, _ = self.request("/api/diagnostics?" + query)
        report = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertEqual(report["device_requested"], "cpu")
        self.assertFalse(report["inference_started"])
        self.assertFalse(report["allow_download"])
        self.assertTrue(report["downloads_default_off"])

    def test_invalid_job_id_is_rejected(self) -> None:
        status, body, _ = self.request("/api/jobs/not-a-job-id")
        self.assertEqual(status, 400)
        self.assertIn("Identificador de trabajo no válido", json.loads(body.decode("utf-8"))["error"])


if __name__ == "__main__":
    unittest.main()
