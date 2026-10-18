from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ImageModelContractTests(unittest.TestCase):
    def test_generator_spatial_seed_matches_64_by_96_training_tensor(self) -> None:
        networks = (ROOT / "ml" / "networks.py").read_text(encoding="utf-8")
        trainer = (ROOT / "ml" / "train.py").read_text(encoding="utf-8")
        # A 6x4 seed with four 2x upscales yields tensor [N,C,96,64],
        # which corresponds to a 64x96 (width x height) PNG.
        self.assertIn("base_channels * 6 * 4", networks)
        self.assertIn("view(-1, self.base_channels, 6, 4)", networks)
        self.assertIn("IMAGE_SIZE = (64, 96)", trainer)

    def test_model_code_does_not_load_pretrained_generator_weights(self) -> None:
        trainer = (ROOT / "ml" / "train.py").read_text(encoding="utf-8")
        networks = (ROOT / "ml" / "networks.py").read_text(encoding="utf-8")
        self.assertIn('"model_origin": "random-initialization"', trainer)
        self.assertIn("class ConditionalGenerator", networks)
        self.assertNotIn("from_pretrained", trainer + networks)
        self.assertNotIn("safetensors.torch.load_file", trainer + networks)

    def test_training_is_blocked_without_explicit_rights_review(self) -> None:
        trainer = (ROOT / "ml" / "train.py").read_text(encoding="utf-8")
        self.assertIn('"training_permission"', trainer)
        self.assertIn('"license_review"', trainer)
        self.assertIn('"visual_review"', trainer)
        self.assertIn("parser.error", trainer)
