from __future__ import annotations

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "tools" / "image-creator" / "index.html"


class ImageCreatorUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_prompt_is_the_primary_action_and_customization_starts_collapsed(self) -> None:
        prompt_position = self.html.index('id="prompt"')
        result_options_position = self.html.index('<details class="result-settings">')
        advanced_position = self.html.index('<details class="advanced">')
        generate_position = self.html.index('id="generate-button"')
        self.assertLess(prompt_position, result_options_position)
        self.assertLess(result_options_position, advanced_position)
        self.assertLess(advanced_position, generate_position)
        self.assertNotRegex(
            self.html[result_options_position:self.html.index(">", result_options_position)],
            r"\bopen\b",
        )
        self.assertNotRegex(
            self.html[advanced_position:self.html.index(">", advanced_position)],
            r"\bopen\b",
        )

    def test_recommended_character_and_transparency_modes_are_enabled_by_default(self) -> None:
        self.assertRegex(self.html, r'<input id="character-mode" type="checkbox" checked>')
        self.assertRegex(self.html, r'<input id="transparent-background" type="checkbox" checked>')
        self.assertRegex(
            self.html,
            r'<input id="model" name="model"[^>]*value="hakurei/waifu-diffusion"',
        )
        self.assertRegex(self.html, r'<option value="fp16" selected>')
        self.assertRegex(self.html, r'<input id="allow-download" type="checkbox" checked>')
        self.assertRegex(self.html, r'<input id="cpu-threads" type="number" min="1" max="6"[^>]*value="4"')

    def test_diagnostics_are_available_only_inside_advanced_settings(self) -> None:
        advanced_start = self.html.index('<details class="advanced">')
        advanced_end = self.html.index("</details>", advanced_start)
        diagnostics_position = self.html.index('id="diagnose-button"')
        self.assertLess(advanced_start, diagnostics_position)
        self.assertLess(diagnostics_position, advanced_end)
        self.assertIn('id="diagnostics-panel"', self.html[advanced_start:advanced_end])

    def test_prompt_guidance_and_download_disclosure_remain_visible(self) -> None:
        self.assertIn("cabello, cuerpo, pose, piel, ojos, ropa y expresión", self.html)
        self.assertIn("bloqueos automáticos", self.html)
        self.assertIn("La primera generación descarga localmente los pesos necesarios", self.html)
        self.assertIn("id=\"generate-button\"", self.html)
        self.assertIn("outputs/generated", self.html)


if __name__ == "__main__":
    unittest.main()
