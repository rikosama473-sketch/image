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


    def test_center_layer_preserves_imported_dimensions_and_centers_offsets(self) -> None:
        self.assertIn('l.x=Math.round((W-l.w)/2)', self.avatar)
        self.assertIn('l.y=Math.round((H-l.h)/2)', self.avatar)
        self.assertIn('Capa centrada sin cambiar su tamaño ni proporción', self.avatar)
        self.assertNotIn('if(l){l.x=0;l.y=0;l.w=W;l.h=H;render();}', self.avatar)

    def test_manual_editor_round_trips_editable_layers_and_provenance(self) -> None:
        self.assertIn('async function saveProject()', self.manual)
        self.assertIn('app:"IMAGE Manual Character Editor"', self.manual)
        self.assertIn('png:l.canvas.toDataURL("image/png")', self.manual)
        self.assertIn('backup:l.backup.toDataURL("image/png")', self.manual)
        self.assertIn('sourceTransform:l.sourceTransform?Object.assign({},l.sourceTransform):null', self.manual)
        self.assertIn('async function openProject(file)', self.manual)
        self.assertIn('canvas:await loadCanvasUrl(l.png)', self.manual)
        self.assertIn('backup:await loadCanvasUrl(l.backup||l.png)', self.manual)
        self.assertIn('mctx.drawImage(mask,0,0)', self.manual)
        self.assertIn('Las capas, la selección y su procedencia se recuperaron.', self.manual)

    def test_manual_composite_export_keeps_alpha_and_uses_png(self) -> None:
        self.assertIn('function makeComposite(){const c=makeCanvas(doc.width,doc.height)', self.manual)
        self.assertIn('if(l.visible){ctx.save();ctx.globalAlpha=l.opacity;ctx.drawImage(l.canvas,0,0);ctx.restore();}', self.manual)
        self.assertIn('function exportCanvas(canvas,name,trim)', self.manual)
        self.assertIn('},"image/png")', self.manual)
        self.assertIn('exportCanvas(makeComposite(),"composicion-image.png",false)', self.manual)

    def test_constructor_and_manual_editor_have_project_save_open_controls(self) -> None:
        self.assertIn('function save(){const data={schemaVersion:2,app:"IMAGE Character Creator"', self.avatar)
        self.assertIn('function load(file){const r=new FileReader()', self.avatar)
        self.assertIn('$(\"saveProjectBtn\").addEventListener("click",saveProject)', self.manual)
        self.assertIn('$(\"openProjectBtn\").addEventListener("click",function(){$("projectFile").click();})', self.manual)


if __name__ == "__main__":
    unittest.main()
