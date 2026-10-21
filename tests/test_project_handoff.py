"""Regression checks for project handoff between IMAGE editor modules."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ImageProjectHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.avatar = (ROOT / "tools/avatar-maker/index.html").read_text(encoding="utf-8")
        cls.manual = (ROOT / "tools/manual-character-editor/index.html").read_text(encoding="utf-8")
        cls.workbench = (ROOT / "tools/hairstyle-workbench/index.html").read_text(encoding="utf-8")
        cls.status = (ROOT / "docs/DEVELOPMENT_STATUS.md").read_text(encoding="utf-8")

    def test_constructor_saves_base_illustration_source_and_filter(self) -> None:
        self.assertIn("baseSource:activeLook().src", self.avatar)
        self.assertIn("baseLabel:activeLook().label", self.avatar)
        self.assertIn("baseSourceReview:", self.avatar)
        self.assertIn("baseFilter:currentBaseFilter()", self.avatar)

    def test_manual_editor_dispatches_both_source_project_schemas(self) -> None:
        self.assertIn('data.app==="IMAGE Character Creator"', self.manual)
        self.assertIn('data.app==="IMAGE Hairstyle Workbench"', self.manual)
        self.assertIn("await importCharacterCreatorProject(data)", self.manual)
        self.assertIn("await importHairstyleWorkbenchProject(data)", self.manual)
        self.assertIn('data.app!=="IMAGE Manual Character Editor"', self.manual)

    def test_import_only_allows_embedded_images_or_safe_repository_paths(self) -> None:
        self.assertIn('startsWith("../../")', self.manual)
        self.assertIn("decodeURIComponent(relative)", self.manual)
        self.assertIn('part===".."', self.manual)
        self.assertIn("Por seguridad, el editor solo acepta imágenes incrustadas o rutas locales", self.manual)
        self.assertIn("MAX_IMPORTED_PROJECT_BYTES=120*1024*1024", self.manual)
        self.assertIn("MAX_IMPORTED_PROJECT_TOTAL_LAYER_PIXELS=80000000", self.manual)
        self.assertIn("function checkImportedLayerBudget(", self.manual)
        self.assertIn("checkImportedLayerBudget(dimensions.width,dimensions.height", self.manual)

    def test_source_metadata_is_saved_and_restored(self) -> None:
        for field in ("sourceApp", "sourceLayerId", "sourceCategory", "sourceStatus", "sourceTags", "sourcePath", "sourceTransform"):
            with self.subTest(field=field):
                self.assertIn(field + ":", self.manual)
                self.assertIn("l." + field, self.manual)

    def test_full_illustration_and_unmigrated_variants_are_labelled_honestly(self) -> None:
        self.assertIn('sourceCategory:"full_illustration"', self.manual)
        self.assertIn("no se inventaron capas semánticas", self.manual)
        self.assertIn("Las variantes adicionales siguen en el JSON original", self.manual)
        self.assertIn("proyecto del Constructor es antiguo y no registra la imagen base", self.manual)

    def test_workbench_original_schema_remains_available(self) -> None:
        self.assertIn('app:"IMAGE Hairstyle Workbench"', self.workbench)
        self.assertIn("layers:layers.map(serialLayer)", self.workbench)
        self.assertIn("styles:styles.map(serialStyle)", self.workbench)


if __name__ == "__main__":
    unittest.main()
