from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import audit_dataset  # noqa: E402


class DatasetAuditTests(unittest.TestCase):
    def test_filename_origin_hint_is_conservative(self) -> None:
        self.assertIn("verify account/origin", audit_dataset.filename_origin_hint("from-PixAI-123-0.png"))
        self.assertIn("preserve exact name", audit_dataset.filename_origin_hint("from-PixAI-123-0.png"))
        self.assertIn("origin unknown", audit_dataset.filename_origin_hint("17.png"))
        self.assertIn("unknown", audit_dataset.filename_origin_hint("portrait.png"))

    def test_alpha_fraction_is_reported_without_mutating_image(self) -> None:
        image = Image.new("RGBA", (2, 2), (200, 10, 30, 255))
        image.putpixel((0, 0), (200, 10, 30, 0))
        before = image.getpixel((0, 0))
        has_alpha, fraction = audit_dataset.alpha_opaque_fraction(image)
        self.assertTrue(has_alpha)
        self.assertAlmostEqual(float(fraction), 0.75)
        self.assertEqual(image.getpixel((0, 0)), before)

    def test_average_hash_is_stable(self) -> None:
        image = Image.new("RGB", (12, 12), (255, 255, 255))
        self.assertEqual(audit_dataset.average_hash(image), audit_dataset.average_hash(image.copy()))
        self.assertEqual(len(audit_dataset.average_hash(image)), 16)

    def test_audit_reports_dimensions_sha_and_never_deletes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "from-PixAI-1.png"
            Image.new("RGBA", (20, 30), (10, 20, 30, 255)).save(image_path)
            record = audit_dataset.audit_one(image_path, root, {})
            self.assertEqual(record["width"], "20")
            self.assertEqual(record["height"], "30")
            self.assertEqual(record["has_alpha"], "true")
            self.assertEqual(len(record["sha256"]), 64)
            self.assertTrue(image_path.exists())
            self.assertEqual(record["training_permission"], "unreviewed")


if __name__ == "__main__":
    unittest.main()
