from __future__ import annotations
import sys
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
from generation_presets import BASE_NEGATIVE_PROMPT, CHARACTER_ONLY_NEGATIVE_PROMPT, RECOMMENDED_MODEL_ID, RECOMMENDED_MODEL_REVISION, RECOMMENDED_MODEL_VARIANT, build_generation_prompts  # noqa: E402

class GenerationPresetTests(unittest.TestCase):
    def test_recommended_model_is_preconfigured(self):
        self.assertEqual(RECOMMENDED_MODEL_ID, "hakurei/waifu-diffusion")
        self.assertEqual(RECOMMENDED_MODEL_REVISION, "main")
        self.assertEqual(RECOMMENDED_MODEL_VARIANT, "fp16")
    def test_character_prompt_blocks_common_non_character_extras(self):
        positive, negative = build_generation_prompts("silver hair, blue eyes")
        self.assertIn("one anime character", positive)
        self.assertIn("plain pure white background", positive)
        for term in ("bad anatomy", "multiple people", "aura", "emojis", "watermark"):
            self.assertIn(term, negative)
    def test_user_negatives_are_additive(self):
        _, negative = build_generation_prompts("anime girl", "hat, sword")
        self.assertIn(BASE_NEGATIVE_PROMPT, negative)
        self.assertIn(CHARACTER_ONLY_NEGATIVE_PROMPT, negative)
        self.assertTrue(negative.endswith("hat, sword"))
    def test_transparency_off_does_not_add_white_background_instruction(self):
        positive, negative = build_generation_prompts("anime portrait", character_mode=True, transparent_background=False)
        self.assertIn("one anime character", positive)
        self.assertNotIn("plain pure white background", positive)
        self.assertIn("multiple characters", negative)
    def test_character_mode_can_be_disabled_without_dropping_anatomy_negatives(self):
        positive, negative = build_generation_prompts("anime portrait", character_mode=False, transparent_background=False)
        self.assertEqual(positive, "anime portrait")
        self.assertIn("bad anatomy", negative)
        self.assertNotIn("multiple people", negative)
    def test_empty_prompt_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "descripción"):
            build_generation_prompts("  ")
if __name__ == "__main__":
    unittest.main()
