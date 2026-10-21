#!/usr/bin/env python3
"""Merge a browser-exported IMAGE visual-reference bundle into the repository store.

Usage:
    python scripts/apply_visual_reference_annotations.py image-visual-reference-library-export.json

Web images stay linked to their sources. This script only writes labels, tags,
review states, user reference links, and style-recipe metadata.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "tools/visual-reference-library/annotations.json"
BACKUP_DIR = ROOT / "generated/visual-reference-backups"


def fail(message: str) -> None:
    raise SystemExit("ERROR: " + message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        fail(f"Cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"Expected a JSON object in {path}")
    return value


def merge_records(base: list[dict[str, Any]], updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in base + updates:
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id.strip():
            result[record_id] = record
    return list(result.values())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="JSON exported by the visual-reference browser")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Repository annotation store")
    parser.add_argument("--no-backup", action="store_true", help="Do not back up an existing annotation file")
    args = parser.parse_args()

    source = args.bundle if args.bundle.is_absolute() else (Path.cwd() / args.bundle).resolve()
    output = args.output if args.output.is_absolute() else (ROOT / args.output).resolve()
    try:
        output.relative_to(ROOT)
    except ValueError:
        fail("Output must be inside the repository root.")

    incoming = load_json(source)
    if incoming.get("schema_version") != 1:
        fail("Only schema_version 1 exports are supported.")
    annotations = incoming.get("annotations", {})
    references = incoming.get("references_added_by_user", incoming.get("user_references", []))
    styles = incoming.get("style_recipes", [])
    if not isinstance(annotations, dict) or not isinstance(references, list) or not isinstance(styles, list):
        fail("The export must contain annotations (object), references_added_by_user (array), and style_recipes (array).")

    valid_references: list[dict[str, Any]] = []
    for ref in references:
        if not isinstance(ref, dict):
            fail("Every user reference must be a JSON object.")
        if not ref.get("id") or not ref.get("title") or not str(ref.get("source_url", "")).startswith("https://"):
            fail(f"User reference {ref.get('id')} requires ID, title, and HTTPS source URL.")
        valid_references.append(ref)
    for style in styles:
        if not isinstance(style, dict) or not style.get("id") or not style.get("name"):
            fail("Each style recipe must be an object with non-empty id and name.")
        if style.get("image_generated") is True:
            fail(f"Recipe {style.get('id')} cannot claim a generated image from a metadata-only browser.")

    current = load_json(output) if output.is_file() else {
        "schema_version": 1,
        "project": "IMAGE visual reference library",
        "annotations": {},
        "user_references": [],
        "style_recipes": [],
    }
    if current.get("schema_version") != 1:
        fail("The existing repository annotation store uses an unsupported schema version.")

    merged_annotations = dict(current.get("annotations", {}))
    merged_annotations.update(annotations)

    if output.exists() and not args.no_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup = BACKUP_DIR / f"annotations-{stamp}.json"
        shutil.copy2(output, backup)
        print(f"Backup: {backup.relative_to(ROOT)}")

    result = {
        "schema_version": 1,
        "project": "IMAGE visual reference library",
        "updated": datetime.now(timezone.utc).isoformat(),
        "annotations": merged_annotations,
        "user_references": merge_records(current.get("user_references", []), valid_references),
        "style_recipes": merge_records(current.get("style_recipes", []), styles),
        "notice": "Metadata only. Web image references remain linked to their original sources; rights must be checked individually.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved {len(result['annotations'])} annotated records, "
        f"{len(result['user_references'])} user references, and "
        f"{len(result['style_recipes'])} style recipes to {output.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
