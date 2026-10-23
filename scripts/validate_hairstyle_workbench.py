#!/usr/bin/env python3
"""Static checks for IMAGE's manual hairstyle workbench (no network or image generation)."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools" / "hairstyle-workbench" / "index.html"
TAXONOMY = ROOT / "tools" / "hairstyle-workbench" / "hair-style-taxonomy.json"
LIBRARY_JSON = ROOT / "tools" / "hairstyle-workbench" / "hairstyle-library.json"
LIBRARY_JS = ROOT / "tools" / "hairstyle-workbench" / "hairstyle-library.js"
WEB_REFERENCES = ROOT / "tools" / "hairstyle-workbench" / "hairstyle-web-references.json"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not PAGE.is_file():
        fail(f"Missing page: {PAGE}")
    if not TAXONOMY.is_file():
        fail(f"Missing taxonomy: {TAXONOMY}")
    if not LIBRARY_JSON.is_file():
        fail(f"Missing recipe library: {LIBRARY_JSON}")
    if not LIBRARY_JS.is_file():
        fail(f"Missing recipe viewer script: {LIBRARY_JS}")
    if not WEB_REFERENCES.is_file():
        fail(f"Missing web reference catalog: {WEB_REFERENCES}")

    html = PAGE.read_text(encoding="utf-8")
    required = (
        "Cargar muestra por capas",
        "Guardar como variante",
        "Duplicar variante",
        "Importar pieza PNG transparente",
        "Exportar PNG",
        "manual_only:true",
        "data-preview",
        "pieceTags",
        "tools/avatar-maker/assets/catalog.json",
        "no llama a ninguna IA ni a una API",
        'src="./hairstyle-library.js"',
    )
    missing = [marker for marker in required if marker not in html]
    if missing:
        fail("The manual workbench is missing required features: " + ", ".join(missing))

    # This page may load its same-repository catalogue, but must not call external
    # generative endpoints or require a provider key.
    forbidden = ("api.openai.com", "OPENAI_API_KEY", "generations.create", "images.edit")
    found = [marker for marker in forbidden if marker in html]
    if found:
        fail("The no-AI workbench contains provider/API code: " + ", ".join(found))
    viewer = LIBRARY_JS.read_text(encoding="utf-8")
    for marker in ("hairstyle-web-references.json", "function renderWebReferences", "referencesTab", "overlayModeField", "overlayMode", "parts_same_base", "parts_realignable"):
        if marker not in viewer:
            fail("The web-reference gallery is missing integration marker: " + marker)
    viewer_forbidden = [marker for marker in forbidden if marker in viewer]
    if viewer_forbidden:
        fail("The recipe viewer contains provider/API code: " + ", ".join(viewer_forbidden))

    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    if not scripts:
        fail("No inline JavaScript block was found.")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        temporary_script = Path(handle.name)
        handle.write("\n".join(scripts))
    try:
        result = subprocess.run(
            ["node", "--check", str(temporary_script)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            fail("JavaScript syntax error: " + (result.stderr.strip() or result.stdout.strip()))
    finally:
        temporary_script.unlink(missing_ok=True)

    result = subprocess.run(
        ["node", "--check", str(LIBRARY_JS)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        fail("Recipe viewer JavaScript syntax error: " + (result.stderr.strip() or result.stdout.strip()))

    try:
        library = json.loads(LIBRARY_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Recipe library JSON is invalid: {exc}")
    recipes = library.get("recipes")
    if library.get("schema_version") != 1 or not isinstance(recipes, list) or len(recipes) != 120:
        fail("Recipe library must have schema version 1 and exactly 120 recipes.")
    recipe_ids = [recipe.get("id") for recipe in recipes]
    recipe_names = [recipe.get("name") for recipe in recipes]
    if len(set(recipe_ids)) != 120 or len(set(recipe_names)) != 120:
        fail("Recipe IDs and names must be unique; similar designs must remain separately stored.")
    allowed_slots = {"haircut", "bangs", "sidelocks", "tie", "ahoge", "accessory"}
    for recipe in recipes:
        components = recipe.get("components")
        if recipe.get("visual_status") != "schematic_only" or recipe.get("do_not_deduplicate") is not True:
            fail(f"Recipe {recipe.get('id')} is missing schematic-only or retention metadata.")
        if not isinstance(components, list) or not any(part.get("slot") == "haircut" for part in components):
            fail(f"Recipe {recipe.get('id')} must include a base haircut component.")
        if any(part.get("slot") not in allowed_slots or not part.get("tags") for part in components):
            fail(f"Recipe {recipe.get('id')} contains a component without a supported slot or tags.")
    requested_combo = ("short_hair", "long_sidelocks", "side_ponytail", "ahoge")
    if not any(all(tag in recipe.get("tags", []) for tag in requested_combo) for recipe in recipes):
        fail("The example combination short hair + long side lock + side ponytail + ahoge is missing.")

    try:
        web_references = json.loads(WEB_REFERENCES.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Web reference catalogue JSON is invalid: {exc}")
    web_items = web_references.get("items")
    if web_references.get("schema_version") != 1 or not isinstance(web_items, list) or len(web_items) < 40:
        fail("Web reference catalogue must have schema version 1 and at least 10 records.")
    web_ids = [item.get("id") for item in web_items]
    if len(web_ids) != len(set(web_ids)):
        fail("Web reference IDs must be unique.")
    downloadable = [item for item in web_items if item.get("usable_asset") is True]
    references_only = [item for item in web_items if item.get("usable_asset") is False]
    if not downloadable or not references_only:
        fail("The web catalogue must separate usable-asset records from visual references.")
    allowed_overlay_modes = {"parts_same_base", "parts_realignable", "reference_only"}
    for item in web_items:
        if not item.get("source_url", "").startswith("https://") or not item.get("license_status"):
            fail("Every web record must include an HTTPS source and explicit license status.")
        if item.get("usable_asset") and not item.get("asset_download_url"):
            fail("Every usable-asset record must include a downloadable asset URL or source page.")
        if item.get("overlay_mode") not in allowed_overlay_modes or not item.get("overlay_notes"):
            fail(f"Record {item.get('id')} must explicitly classify how it can be mounted over a base.")
    by_id = {item.get("id"): item for item in web_items}
    if by_id.get("asset-hmlf001-layered-png", {}).get("overlay_mode") != "parts_same_base":
        fail("The layered HMLF001 pack must be marked as compatible-base-only, not universal.")
    if by_id.get("asset-cc0-portraits", {}).get("overlay_mode") != "parts_same_base":
        fail("The CC0 XCF portrait pack must be marked as base-specific.")
    if any(by_id.get(ref_id, {}).get("visual_review") != "pending" for ref_id in ("user-pin-hairstyle-reference-a", "user-pin-hairstyle-reference-b")):
        fail("User-provided Pinterest images must remain pending visual and rights review.")

    # The selected art direction is anime production line art inspired by Madhouse
    # and Trigger. Color is deliberately not a requirement; style fit is.
    art_direction = web_references.get("art_direction", {})
    if art_direction.get("id") != "anime-tv-production-lineart" or art_direction.get("color_required") is not False:
        fail("The art direction must prioritize anime production line art and allow monochrome references.")
    matching = [item for item in web_items if item.get("style_fit") in {"target", "compatible"}]
    target = [item for item in matching if item.get("style_fit") == "target"]
    compatible = [item for item in matching if item.get("style_fit") == "compatible"]
    if len(matching) < 12 or not target or not compatible:
        fail("The gallery needs at least 12 style-matched records, including anchor and compatible references.")
    studios = {item.get("studio_anchor") for item in target}
    if "MADHOUSE" not in studios or "TRIGGER" not in studios:
        fail("The matched collection must include both Madhouse and Trigger visual anchors.")
    if any(item.get("color_required") is True for item in matching):
        fail("Color must not be required for any style-matched reference.")
    if not any(item.get("image_url") for item in target) or not any(item.get("image_url") for item in compatible):
        fail("Both anchor and compatible style groups must have image previews.")
    if 'activeViewerTab="references"' not in viewer or "Hojas y piezas visuales" not in viewer or "Para montar sobre una base plana" not in viewer:
        fail("The viewer must open directly on the visual references gallery and explain overlay compatibility.")

    try:
        taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Taxonomy JSON is invalid: {exc}")
    if taxonomy.get("schema_version") != 1:
        fail("Unexpected taxonomy schema version.")
    if taxonomy.get("retention_policy", {}).get("no_deduplication") is None:
        fail("Taxonomy must explicitly preserve visually similar variants.")
    groups = taxonomy.get("groups")
    if not isinstance(groups, list) or not groups:
        fail("Taxonomy must contain groups of tags.")
    tags = [tag.get("tag") for group in groups for tag in group.get("tags", [])]
    if len(tags) < 30 or any(not isinstance(tag, str) or not tag for tag in tags):
        fail("Taxonomy entries are missing or too few.")
    if len(tags) != len(set(tags)):
        fail("A taxonomy tag is duplicated; review its canonical name.")

    print(
        "PASS: manual hairstyle workbench, inline JavaScript, local-only behavior, "
        f"{len(tags)} taxonomy tags, {len(recipes)} unique recipes, "
        f"{len(web_items)} web references ({len(downloadable)} asset sources), explicit layer-compatibility labels, and valid viewer JavaScript."
    )


if __name__ == "__main__":
    main()
