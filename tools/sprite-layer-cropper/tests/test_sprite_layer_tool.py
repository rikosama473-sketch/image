import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from sprite_layer_tool import process


class SpriteLayerToolTests(unittest.TestCase):
    def test_slices_cells_into_uniform_transparent_pngs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "sheet.png"
            config_path = root / "grid.json"
            output_path = root / "output"

            # Two 8x8 cells: opaque red body, opaque blue hair.
            sheet = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
            for x in range(8):
                for y in range(8):
                    sheet.putpixel((x, y), (255, 0, 0, 255))
                    sheet.putpixel((x + 8, y), (0, 0, 255, 255))
            sheet.save(input_path)

            config_path.write_text(json.dumps({
                "grid": {"rows": 1, "columns": 2},
                "output": {"width": 32, "height": 32},
                "cells": [
                    {"row": 1, "column": 1, "layer": "body"},
                    {"row": 1, "column": 2, "layer": "hair"}
                ]
            }), encoding="utf-8")

            manifest = process(input_path, config_path, output_path)
            self.assertEqual(len(manifest["assets"]), 2)
            self.assertEqual(manifest["errors"], [])

            body = Image.open(output_path / "body/r01_c01_body.png").convert("RGBA")
            hair = Image.open(output_path / "hair/r01_c02_hair.png").convert("RGBA")
            self.assertEqual(body.size, (32, 32))
            self.assertEqual(hair.size, (32, 32))
            self.assertEqual(body.getchannel("A").getbbox(), (0, 0, 32, 32))
            self.assertEqual(hair.getchannel("A").getbbox(), (0, 0, 32, 32))
            self.assertEqual(json.loads((output_path / "manifest.json").read_text())["source_dimensions"], [16, 8])

    def test_rejects_cell_outside_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "sheet.png"
            config = root / "grid.json"
            Image.new("RGBA", (8, 8), (255, 255, 255, 255)).save(source)
            config.write_text(json.dumps({
                "grid": {"rows": 1, "columns": 1},
                "cells": [{"row": 2, "column": 1, "layer": "body"}]
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                process(source, config, root / "out")


if __name__ == "__main__":
    unittest.main()
