#!/usr/bin/env python3
"""Validate the IMAGE visual-reference workbench and reference-catalog metadata."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools/visual-reference-library/index.html"
CATALOG = ROOT / "tools/visual-reference-library/reference-library.json"
CONTACT_SHEETS = ROOT / "scripts/build_visual_contact_sheets.py"


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def main() -> None:
    for path in (PAGE, CATALOG, CONTACT_SHEETS):
        if not path.is_file():
            fail(f"Missing required file: {path.relative_to(ROOT)}")

    html = PAGE.read_text(encoding="utf-8")
    for marker in (
        "reference-library.json",
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
        ast.parse(CONTACT_SHEETS.read_text(encoding="utf-8"), filename=str(CONTACT_SHEETS))
    except SyntaxError as exc:
        fail(f"Contact sheet script syntax error: {exc}")
    print(
        "PASS: visual reference browser syntax; "
        f"{len(items)} seeded web references; contact-sheet script syntax."
    )


if __name__ == "__main__":
    main()
