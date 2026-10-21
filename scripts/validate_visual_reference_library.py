#!/usr/bin/env python3
"""Validate the IMAGE visual-reference workbench and reference-catalog metadata."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools/visual-reference-library/index.html"
AVATAR_PAGE = ROOT / "tools/avatar-maker/index.html"
CATALOG = ROOT / "tools/visual-reference-library/reference-library.json"
ANNOTATIONS = ROOT / "tools/visual-reference-library/annotations.json"
CONTACT_SHEETS = ROOT / "scripts/build_visual_contact_sheets.py"
ANNOTATION_APPLIER = ROOT / "scripts/apply_visual_reference_annotations.py"
LAUNCHER = ROOT / "tools/visual-reference-library/start-visual-reference-library.bat"


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def main() -> None:
    for path in (PAGE, AVATAR_PAGE, CATALOG, ANNOTATIONS, CONTACT_SHEETS, ANNOTATION_APPLIER, LAUNCHER):
        if not path.is_file():
            fail(f"Missing required file: {path.relative_to(ROOT)}")

    html = PAGE.read_text(encoding="utf-8")
    for marker in (
        "reference-library.json",
        "annotations.json",
        "apply_visual_reference_annotations.py",
        "bulkSources",
        "importBulkSources",
        "Probar en editor IA",
        "visualPrompt=",
        "../avatar-maker/assets/image-library.json",
        "../avatar-maker/assets/catalog.json",
        "data-tab=\"web\"",
        "data-tab=\"local\"",
        "data-tab=\"layers\"",
        "data-tab=\"styles\"",
        "Crear receta desde selección",
        "Exportar biblioteca JSON",
        "localStorage",
        "reference_only_unverified",
        "No se pudo",
    ):
        if marker not in html:
            fail(f"The visual reference page is missing expected feature marker: {marker}")
    if "api.openai.com" in html or "OPENAI_API_KEY" in html:
        fail("The reference browser must not make paid AI calls or require an API key.")
    inline_scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    if len(inline_scripts) != 1:
        fail("Expected exactly one inline JavaScript block in the visual-reference page.")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        temp_js = Path(handle.name)
        handle.write(inline_scripts[0])
    try:
        result = subprocess.run(["node", "--check", str(temp_js)], text=True, capture_output=True, check=False)
        if result.returncode:
            fail("Inline JavaScript syntax error: " + (result.stderr.strip() or result.stdout.strip()))
    finally:
        temp_js.unlink(missing_ok=True)

    launcher_text = LAUNCHER.read_text(encoding="utf-8")
    if "tools/avatar-maker/ai_edit_server.py" not in launcher_text or "tools/visual-reference-library/index.html" not in launcher_text:
        fail("Windows launcher must open the visual library with the existing local server.")

    avatar_html = AVATAR_PAGE.read_text(encoding="utf-8")
    for marker in ("new URLSearchParams(window.location.search)", "visualPrompt", "visualBackground", "aiNextResultMeta"):
        if marker not in avatar_html:
            fail(f"Character Creator is missing the visual recipe handoff marker: {marker}")

    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Reference JSON is invalid: {exc}")
    items = data.get("items")
    if data.get("schema_version") != 1 or not isinstance(items, list) or len(items) < 8:
        fail("Reference catalog must use schema_version 1 and contain at least 8 seed references.")
    ids = [item.get("id") for item in items]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        fail("Reference IDs must be unique and non-empty.")
    for item in items:
        if not item.get("title") or not item.get("category") or not item.get("source_url", "").startswith("https://"):
            fail(f"Reference {item.get('id')} lacks title, category, or HTTPS source URL.")
        if not item.get("license_status") or item.get("review_status") != "unreviewed":
            fail(f"Reference {item.get('id')} must state rights status and start unreviewed.")
        if item.get("image_url") and not item["image_url"].startswith("https://"):
            fail(f"Reference {item.get('id')} image URL must use HTTPS.")
        if item.get("license_status") == "reference_only_unverified" and item.get("local_asset") is True:
            fail(f"Unverified external reference {item.get('id')} must not be declared as a reusable local asset.")
    if not any("pinterest." in item.get("source_url", "") for item in items):
        fail("At least one Pinterest source must be present.")

    try:
        saved = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Persistent annotation store is invalid JSON: {exc}")
    if saved.get("schema_version") != 1 or not isinstance(saved.get("annotations"), dict):
        fail("Persistent annotation store must use schema_version 1 and an annotations object.")
    if not isinstance(saved.get("user_references"), list) or not isinstance(saved.get("style_recipes"), list):
        fail("Persistent annotation store must include user_references and style_recipes arrays.")

    contact_source = CONTACT_SHEETS.read_text(encoding="utf-8")
    if "near-duplicates-candidates.json" not in contact_source or "near_duplicate_candidate_pairs" not in contact_source:
        fail("Contact-sheet script must report perceptual near-duplicate candidates.")

    for path, label in (
        (CONTACT_SHEETS, "Contact sheet"),
        (ANNOTATION_APPLIER, "Annotation applier"),
    ):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"{label} script syntax error: {exc}")
    # Execute the importer in a temporary directory to verify merging and stable IDs,
    # not merely Python syntax. The temp output stays under ROOT for the path safety check.
    with tempfile.TemporaryDirectory(prefix=".visual-reference-test-", dir=ROOT) as temp_dir:
        temp_root = Path(temp_dir)
        output_path = temp_root / "annotations.json"
        bundle_path = temp_root / "export.json"
        output_path.write_text(
            json.dumps({
                "schema_version": 1,
                "project": "IMAGE visual reference library",
                "annotations": {"asset-1": {"tags": ["old"]}},
                "user_references": [{"id": "ref-1", "title": "Old title", "source_url": "https://www.pinterest.com/pin/123/"}],
                "style_recipes": [{"id": "style-1", "name": "Old recipe"}],
            }),
            encoding="utf-8",
        )
        bundle_path.write_text(
            json.dumps({
                "schema_version": 1,
                "annotations": {"asset-1": {"tags": ["reviewed"]}, "asset-2": {"label": "Ojos rasgados"}},
                "references_added_by_user": [{"id": "ref-1", "title": "Updated title", "source_url": "https://www.pinterest.com/pin/123/"}],
                "style_recipes": [{"id": "style-1", "name": "Updated recipe"}],
            }),
            encoding="utf-8",
        )
        imported = subprocess.run(
            [sys.executable, str(ANNOTATION_APPLIER), str(bundle_path), "--output", str(output_path), "--no-backup"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if imported.returncode:
            fail("Annotation importer self-test failed: " + (imported.stderr.strip() or imported.stdout.strip()))
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        if merged["annotations"].get("asset-1", {}).get("tags") != ["reviewed"] or "asset-2" not in merged["annotations"]:
            fail("Annotation importer did not merge and overwrite annotation records correctly.")
        refs = merged.get("user_references", [])
        styles = merged.get("style_recipes", [])
        if len(refs) != 1 or refs[0].get("title") != "Updated title":
            fail("Annotation importer did not deduplicate the reference by stable ID.")
        if len(styles) != 1 or styles[0].get("name") != "Updated recipe":
            fail("Annotation importer did not deduplicate the recipe by stable ID.")

    print(
        "PASS: visual reference browser syntax; "
        f"{len(items)} seeded web references; persistent annotation schema; "
        "contact-sheet syntax; annotation importer merge self-test."
    )


if __name__ == "__main__":
    main()
