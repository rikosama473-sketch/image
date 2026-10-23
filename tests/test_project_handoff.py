"""Regression checks for project handoff between IMAGE editor modules."""
from __future__ import annotations

import json
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

    def test_ai_workspace_explains_the_no_key_hair_generation_path_and_branch_safety(self) -> None:
        ai_workspace = self.avatar.split("function aiWorkspace(root){", 1)[1].split(
            "function syncAIQuality(){", 1
        )[0]
        self.assertIn("Abrir generador IA gratuito", ai_workspace)
        self.assertIn("generate-character-assets-free.yml", ai_workspace)
        self.assertIn("cuota pública compartida", ai_workspace)
        self.assertIn("work/easy-avatar-maker-2026-10", ai_workspace)
        self.assertIn("hair-core-5", ai_workspace)
        self.assertIn("no ejecutes el proceso sobre main", ai_workspace)
        self.assertNotIn("generate-hairstyle-variants.yml", ai_workspace)

    def test_ai_workspace_renders_reusable_free_generated_hairstyle_variants(self) -> None:
        self.assertIn('id="aiFreeVariantsGrid"', self.avatar)
        self.assertIn('id="aiFreeVariantsReload"', self.avatar)
        self.assertIn("async function refreshAIFreeVariants(force=false)", self.avatar)
        self.assertIn('data-ai-free-asset-id', self.avatar)
        self.assertIn('kind==="generated_full_illustration"', self.avatar)
        self.assertIn('useLibraryAsset(button.dataset.aiFreeAssetId,"ai")', self.avatar)
        self.assertIn("no recortes de cabello aislados", self.avatar)

    def test_existing_free_generated_variants_are_indexed_and_review_pending(self) -> None:
        library = json.loads(
            (ROOT / "tools/avatar-maker/assets/image-library.json").read_text(encoding="utf-8")
        )
        assets = library["assets"]
        hair = [
            item for item in assets
            if item.get("pack") == "hair-core-5"
            and item.get("origin_hint", "").startswith(
                "Generated in repository workflow via the public image-edit Space"
            )
        ]
        expressions = [
            item for item in assets
            if item.get("pack") == "expressions-core-5"
            and item.get("origin_hint", "").startswith(
                "Generated in repository workflow via the public image-edit Space"
            )
        ]
        self.assertEqual(library["asset_count"], len(assets))
        self.assertEqual(len(hair), 5)
        self.assertEqual(len(expressions), 3)
        for item in hair + expressions:
            with self.subTest(asset=item["id"]):
                self.assertEqual(item["kind"], "generated_full_illustration")
                self.assertEqual(item["visual_review"], "needs_visual_identity_review")
                self.assertEqual(item["license_review"], "unreviewed")
                self.assertEqual(item["training_permission"], "unreviewed")
                self.assertTrue((ROOT / item["path"]).is_file(), item["path"])

    def test_ai_generated_hairstyles_can_open_the_extraction_workbench(self) -> None:
        self.assertIn('data-ai-free-extract-id', self.avatar)
        self.assertIn("openLibraryAssetForExtraction(button.dataset.aiFreeExtractId)", self.avatar)
        self.assertIn('state.category="anatomy"', self.avatar)
        self.assertIn("Pintá únicamente el pelo o la pieza", self.avatar)

    def test_reusable_parts_persist_locally_and_can_be_added_back_as_layers(self) -> None:
        for feature in (
            'const LOCAL_PARTS_DB="image-local-parts-v1"',
            "indexedDB.open(LOCAL_PARTS_DB,1)",
            "function persistLocalPart(record)",
            "async function saveSelectedLayerToLocalLibrary()",
            "async function addLocalPartToCanvas(id)",
            "async function renderLocalParts()",
            'id="anatomySavePiece"',
            'id="localPartsGrid"',
            'data-local-part-add',
            'data-local-part-delete',
            'status:"local_saved_candidate"',
        ):
            with self.subTest(feature=feature):
                self.assertIn(feature, self.avatar)
        self.assertIn("Las imágenes no se suben a GitHub ni a una nube", self.avatar)
        self.assertIn('toast("Pieza guardada como "+({hair:"cabello",eyes:"ojos",face:"rostro",body:"cuerpo",clothes:"ropa",accessories:"accesorios"}[category])+" en la biblioteca local.")', self.avatar)


    def test_saved_anatomy_pieces_require_semantic_category_and_keep_source_category(self) -> None:
        self.assertIn('id="anatomyPieceType"', self.avatar)
        self.assertIn('const allowedCategories=["hair","eyes","face","body","clothes","accessories"]', self.avatar)
        self.assertIn('if(!allowedCategories.includes(category))', self.avatar)
        self.assertIn('name:safeName,category,sourceCategory,character:', self.avatar)
        self.assertIn('layer.sourceCategory=sourceCategory;layer.category=category;', self.avatar)
        for category in ("hair", "eyes", "face", "body", "clothes", "accessories"):
            with self.subTest(category=category):
                self.assertIn('value="'+category+'"', self.avatar)

    def test_saved_piece_semantic_category_and_source_provenance_round_trip(self) -> None:
        self.assertIn('sourceCategory:part.sourceCategory||"anatomy"', self.avatar)
        self.assertIn('const categoryLabels={hair:"Cabello",eyes:"Ojos / cejas",face:"Rostro",body:"Cuerpo",clothes:"Ropa",accessories:"Accesorios"}', self.avatar)
        self.assertIn('sourceCategory,character:state.name||"Personaje"', self.avatar)
        self.assertIn('layer.sourceCategory=sourceCategory;layer.category=category;', self.avatar)

    def test_internet_mode_uses_colored_states_and_blocks_unavailable_online_features(self) -> None:
        for feature in (
            'id="internetModeToggle"',
            'id="internetModeLabel"',
            'id="internetModeStatus"',
            '.internet-toggle[data-state=on]',
            '.internet-toggle[data-state=off]',
            '.internet-toggle[data-state=unavailable]',
            'function syncInternetUI()',
            'async function checkInternetConnection()',
            'function setInternetMode(enabled)',
            'navigator.onLine',
            'isLoopbackHost=host=>',
            'localStorage.setItem(INTERNET_MODE_KEY',
            'https://api.github.com/repos/rikosama473-sketch/image',
            'internet-blocked',
            'data-requires-internet="true" id="aiRun"',
            'data-requires-internet="true" id="anatomyGenerate"',
            'data-requires-internet="true" id="anatomyPose"',
            'Los enlaces y acciones online quedan inactivos',
        ):
            with self.subTest(feature=feature):
                self.assertIn(feature, self.avatar)
        self.assertIn('document.addEventListener("click",event=>', self.avatar)
        self.assertIn("internetModeEnabled", self.avatar)
        self.assertIn("las capas y la exportación siguen siendo locales", self.avatar)


if __name__ == "__main__":
    unittest.main()
