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


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not PAGE.is_file():
        fail(f"Missing page: {PAGE}")
    if not TAXONOMY.is_file():
        fail(f"Missing taxonomy: {TAXONOMY}")

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

    scripts = re.findall(r"<script>([\\s\\S]*?)</script>", html)
    if not scripts:
        fail("No inline JavaScript block was found.")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        temporary_script = Path(handle.name)
        handle.write("\\n".join(scripts))
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
        f"and {len(tags)} tags across {len(groups)} taxonomy groups."
    )


if __name__ == "__main__":
    main()
