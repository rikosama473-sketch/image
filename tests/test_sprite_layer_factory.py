from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from split_sprite_sheet import grid_boxes, load_explicit_boxes, normalize_asset, remove_connected_key_color, safe_slug, validate_boxes  # noqa: E402


class SpriteLayerFactoryTests(unittest.TestCase):
    def test_grid_boxes_cover_remainder_pixels_without_gaps(self) -> None:
        boxes = grid_boxes((101, 53), 4, 3, "pibra-hair", "hair")
        self.assertEqual(len(boxes), 12)
        self.assertEqual(boxes[0]["bbox"], [0, 0, 25, 17])
        self.assertEqual(boxes[-1]["bbox"], [75, 35, 26, 18])
        validate_boxes(boxes, (101, 53))

    def test_connected_background_removal_preserves_disconnected_white_details(self) -> None:
        image = Image.new("RGBA", (8, 8), (255, 255, 255, 255))
        for y in range(2, 6):
            for x in range(2, 6):
                image.putpixel((x, y), (20, 40, 80, 255))
        image.putpixel((3, 3), (255, 255, 255, 255))
        result, removed = remove_connected_key_color(image, (255, 255, 255), 0)
        self.assertEqual(result.getpixel((0, 0))[3], 0)
        self.assertEqual(result.getpixel((3, 3))[3], 255)
        self.assertGreater(removed, 0)

    def test_normalization_has_uniform_canvas_and_alpha(self) -> None:
        image = Image.new("RGBA", (20, 10), (0, 0, 0, 0))
        for y in range(2, 8):
            for x in range(5, 15):
                image.putpixel((x, y), (240, 40, 120, 255))
        result, details = normalize_asset(image, (64, 64), trim_alpha=True)
        self.assertEqual(result.size, (64, 64))
        self.assertEqual(result.mode, "RGBA")
        self.assertGreater(details["transparent_pixel_ratio"], 0.3)
        self.assertTrue(details["trimmed_alpha_bounds"])

    def test_boxes_json_validation_and_safe_slugs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "boxes.json"
            path.write_text(json.dumps({"assets": [
                {"id": "Pibra side braid", "category": "Hair Styles", "bbox": [1, 2, 10, 11]}
            ]}), encoding="utf-8")
            parsed = load_explicit_boxes(path)
            self.assertEqual(parsed[0]["id"], "pibra-side-braid")
            self.assertEqual(parsed[0]["category"], "hair-styles")
            self.assertEqual(parsed[0]["bbox"], [1, 2, 10, 11])
        with self.assertRaises(ValueError):
            safe_slug("../escape", "id")

    def test_cli_writes_images_contact_sheet_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "spritesheet.png"
            image = Image.new("RGBA", (20, 10), (255, 255, 255, 255))
            for y in range(1, 9):
                for x in range(1, 9):
                    image.putpixel((x, y), (220, 40, 90, 255))
                for x in range(11, 19):
                    image.putpixel((x, y), (50, 100, 220, 255))
            image.save(source)
            boxes = root / "boxes.json"
            boxes.write_text(json.dumps({"assets": [
                {"id": "hair-bob", "category": "hair", "name": "Bob", "bbox": [0, 0, 10, 10]},
                {"id": "hair-braid", "category": "hair", "name": "Braid", "bbox": [10, 0, 10, 10]}
            ]}), encoding="utf-8")
            out = root / "out"
            subprocess.run([
                sys.executable, str(ROOT / "scripts" / "split_sprite_sheet.py"),
                "--input", str(source), "--output", str(out), "--boxes-json", str(boxes),
                "--canvas", "32x32", "--key-color", "#FFFFFF", "--key-tolerance", "0",
                "--source-url", "https://example.org/original", "--license", "user-owned"
            ], check=True, capture_output=True, text=True)
            self.assertTrue((out / "hair" / "hair-bob.png").is_file())
            self.assertTrue((out / "hair" / "hair-braid.png").is_file())
            self.assertTrue((out / "contact-sheet.png").is_file())
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["license"], "user-owned")
            self.assertEqual(len(manifest["assets"]), 2)
            self.assertTrue(manifest["assets"][0]["sha256"])
            self.assertEqual(manifest["assets"][0]["dimensions"], [32, 32])

    def test_default_refuses_to_overwrite_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.png"
            Image.new("RGBA", (8, 8), (10, 20, 30, 255)).save(source)
            out = root / "out"
            cmd = [sys.executable, str(ROOT / "scripts" / "split_sprite_sheet.py"), "--input", str(source), "--output", str(out), "--grid", "1x1"]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to overwrite", result.stderr)


if __name__ == "__main__":
    unittest.main()
