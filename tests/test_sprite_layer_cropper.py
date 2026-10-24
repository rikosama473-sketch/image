"""Regression tests for the local IMAGE sprite-sheet cropper.

This file lives in the repository's root test suite so normal CI discovers it.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

CROPPER_DIR = Path(__file__).resolve().parents[1] / "tools" / "sprite-layer-cropper"
sys.path.insert(0, str(CROPPER_DIR))
from sprite_layer_tool import process  # noqa: E402


class SpriteLayerCropperIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "sheet.png"
        self.config = self.root / "grid.json"
        self.output = self.root / "out"

    def tearDown(self):
        self.temp.cleanup()

    def config_write(self, data):
        self.config.write_text(json.dumps(data), encoding="utf-8")

    def base_grid(self, **extra):
        data = {"grid": {"rows": 1, "columns": 1},
                "output": {"width": 32, "height": 32},
                "cells": [{"row": 1, "column": 1, "layer": "hair"}]}
        data.update(extra)
        return data

    def test_exports_uniform_rgba_png_and_manifest(self):
        Image.new("RGBA", (8, 8), (10, 20, 200, 255)).save(self.source)
        self.config_write(self.base_grid())
        manifest = process(self.source, self.config, self.output)
        path = self.output / "hair/r01_c01_hair.png"
        with Image.open(path) as image:
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.size, (32, 32))
            self.assertEqual(image.getchannel("A").getbbox(), (0, 0, 32, 32))
        self.assertEqual(manifest["errors"], [])
        self.assertEqual(manifest["assets"][0]["source_bbox_xyxy"], [0, 0, 8, 8])
        saved_manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved_manifest["source_dimensions"], [8, 8])

    def test_region_bbox_crops_local_coordinates_inside_cell(self):
        Image.new("RGBA", (8, 8), (230, 20, 30, 255)).save(self.source)
        self.config_write({
            "grid": {"rows": 1, "columns": 1},
            "output": {"width": 16, "height": 16},
            "regions": [{"row": 1, "column": 1, "layer": "hair", "bbox": [2, 1, 4, 5]}]
        })
        manifest = process(self.source, self.config, self.output)
        self.assertEqual(manifest["assets"][0]["source_bbox_xyxy"], [2, 1, 6, 6])
        self.assertEqual(manifest["assets"][0]["size"], [16, 16])

    def test_rejects_path_traversal_layer_name(self):
        Image.new("RGBA", (8, 8), (1, 2, 3, 255)).save(self.source)
        self.config_write({
            "grid": {"rows": 1, "columns": 1},
            "cells": [{"row": 1, "column": 1, "layer": "../outside"}]
        })
        with self.assertRaisesRegex(ValueError, "Nombre de capa no válido"):
            process(self.source, self.config, self.output)
        self.assertFalse((self.root / "outside").exists())

    def test_rejects_conflicting_cells_and_regions_modes(self):
        Image.new("RGBA", (8, 8), (1, 2, 3, 255)).save(self.source)
        self.config_write({
            "grid": {"rows": 1, "columns": 1},
            "cells": [{"row": 1, "column": 1, "layer": "hair"}],
            "regions": [{"row": 1, "column": 1, "layer": "eyes", "bbox": [0, 0, 2, 2]}]
        })
        with self.assertRaisesRegex(ValueError, "no ambos"):
            process(self.source, self.config, self.output)

    def test_rejects_duplicate_output_targets(self):
        Image.new("RGBA", (8, 8), (1, 2, 3, 255)).save(self.source)
        self.config_write({
            "grid": {"rows": 1, "columns": 1},
            "cells": [
                {"row": 1, "column": 1, "layer": "hair"},
                {"row": 1, "column": 1, "layer": "hair"}
            ]
        })
        with self.assertRaisesRegex(ValueError, "Asignación duplicada"):
            process(self.source, self.config, self.output)

    def test_transparent_pixels_with_rgb_data_are_treated_as_empty(self):
        Image.new("RGBA", (8, 8), (255, 0, 255, 0)).save(self.source)
        self.config_write(self.base_grid())
        manifest = process(self.source, self.config, self.output)
        self.assertEqual(manifest["assets"], [])
        self.assertEqual(len(manifest["errors"]), 1)
        self.assertIn("completamente transparente", manifest["errors"][0]["error"])


if __name__ == "__main__":
    unittest.main()
