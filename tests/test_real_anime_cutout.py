"""Tests for the real-inference cutout report and alpha diagnostics."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_real_anime_cutout_inference.py"
SPEC = importlib.util.spec_from_file_location("real_anime_cutout", SCRIPT)
assert SPEC and SPEC.loader
cutout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cutout)


class AlphaMetricsTests(unittest.TestCase):
    def test_reports_transparent_semi_transparent_and_opaque_pixels(self):
        image = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        for x in range(0, 3):
            for y in range(10):
                image.putpixel((x, y), (0, 0, 0, 0))
        for x in range(3, 5):
            for y in range(10):
                image.putpixel((x, y), (255, 0, 0, 128))
        result = cutout.alpha_metrics(image)
        self.assertEqual(result["pixels"], 100)
        self.assertEqual(result["transparent_pixels"], 30)
        self.assertEqual(result["partial_alpha_pixels"], 20)
        self.assertEqual(result["transition_alpha_65_249_pixels"], 20)
        self.assertEqual(result["near_opaque_250_254_pixels"], 0)
        self.assertEqual(result["near_opaque_250_254_percent"], 0.0)
        self.assertEqual(result["opaque_pixels"], 50)
        self.assertTrue(result["alpha_is_non_binary"])
        self.assertTrue(result["alpha_has_transparency"])
        self.assertEqual(result["foreground_bbox_alpha_gt_8"], [3, 0, 10, 10])

    def test_checkerboard_preview_flattens_alpha_without_changing_size(self):
        image = Image.new("RGBA", (48, 48), (255, 0, 0, 128))
        preview = cutout.checkerboard(image, cell=12)
        self.assertEqual(preview.size, image.size)
        self.assertEqual(preview.mode, "RGB")
        self.assertNotEqual(preview.getpixel((0, 0)), preview.getpixel((12, 0)))

    def test_composite_on_preserves_size_and_shows_transparent_background(self):
        image = Image.new("RGBA", (48, 48), (255, 0, 0, 0))
        image.putpixel((24, 24), (255, 0, 0, 255))
        preview = cutout.composite_on(image, (0, 0, 0))
        self.assertEqual(preview.size, image.size)
        self.assertEqual(preview.mode, "RGB")
        self.assertEqual(preview.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(preview.getpixel((24, 24)), (255, 0, 0))

    def test_repo_path_rejects_parent_traversal(self):
        with self.assertRaises(SystemExit):
            cutout.repo_relative_path("../secret.png", "input")


if __name__ == "__main__":
    unittest.main()
