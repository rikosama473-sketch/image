from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "tools" / "image-creator" / "index.html"
JS_PATH = ROOT / "tools" / "image-creator" / "app.js"
PROFILE_DOC = ROOT / "docs" / "LOW_RESOURCE_HARDWARE_PROFILE.md"


class LowResourceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.js = JS_PATH.read_text(encoding="utf-8")
        cls.profile_doc = PROFILE_DOC.read_text(encoding="utf-8")

    def test_profile_control_and_low_cost_defaults_exist(self) -> None:
        self.assertIn('id="low-resource-preset"', self.html)
        self.assertIn('id="width" type="number" min="64" max="2048" step="8" value="512"', self.html)
        self.assertIn('id="height" type="number" min="64" max="2048" step="8" value="512"', self.html)
        self.assertIn('id="steps" type="number" min="1" max="150" value="12"', self.html)
        self.assertIn('id="count" type="number" min="1" max="8" value="1"', self.html)

    def test_profile_uses_cpu_and_single_image_without_enabling_downloads(self) -> None:
        self.assertIn('$("low-resource-preset").addEventListener("click"', self.js)
        self.assertRegex(self.js, r'\$\("device"\)\.value\s*=\s*"cpu"')
        self.assertRegex(self.js, r'\$\("low-memory"\)\.checked\s*=\s*true')
        self.assertRegex(self.js, r'\$\("cpu-offload"\)\.checked\s*=\s*false')
        self.assertNotRegex(self.js, r'\$\("allow-download"\)\.checked\s*=\s*true')

    def test_document_does_not_claim_vulkan_or_real_generation_is_verified(self) -> None:
        self.assertIn("stable-diffusion.cpp", self.profile_doc)
        self.assertIn("no prueba", self.profile_doc.lower())
        self.assertIn("registrar", self.profile_doc.lower())
        self.assertIn("no se descarga", self.profile_doc.lower())


if __name__ == "__main__":
    unittest.main()
