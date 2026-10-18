#!/usr/bin/env python3
"""Synchronize the training-label CSV with local raster files without losing reviews."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "outputs", "runs", "checkpoints", "processed", "cache"}
FIELDS = [
    "path", "size_bytes", "git_blob_sha", "filename_origin_hint", "source_url", "author",
    "base_model_identifier", "lora_identifiers", "lora_weights_or_settings", "visual_review", "license_review", "training_permission", "hair", "clothing", "legs",
    "pose", "background", "notes", "lora_target_identifiers",
]


def origin_hint(path: str) -> str:
    name = Path(path).name
    if name.startswith("from-PixAI-"):
        return "PixAI filename clue; preserve exact name; verify account/origin and record model/LoRA separately"
    if name.lower().endswith(".png") and name[:-4].isdigit():
        return "numeric filename; origin unknown"
    return "unknown; review source"


def should_skip(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part in SKIP_DIRS for part in parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--labels", type=Path, default=Path("data/training-labels.csv"))
    args = parser.parse_args()
    root = args.root.resolve()
    labels_path = args.labels if args.labels.is_absolute() else root / args.labels
    old_rows: dict[str, dict[str, str]] = {}
    if labels_path.exists():
        with labels_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                path = row.get("path", "").strip()
                if path:
                    old_rows[path] = row

    found: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and not should_skip(path, root):
            found[path.relative_to(root).as_posix()] = path

    result: list[dict[str, str]] = []
    new_count = 0
    for relative in sorted(set(old_rows) | set(found)):
        old = old_rows.get(relative, {})
        actual = found.get(relative)
        record = {field: old.get(field, "") or "" for field in FIELDS}
        record["path"] = relative
        if actual is not None:
            record["size_bytes"] = str(actual.stat().st_size)
            record["filename_origin_hint"] = record["filename_origin_hint"] or origin_hint(relative)
            if relative not in old_rows:
                record["visual_review"] = "unreviewed"
                record["license_review"] = "unreviewed"
                record["training_permission"] = "unreviewed"
                record["notes"] = "New image found locally; inspect source and rights before training."
                new_count += 1
        else:
            prior = record.get("notes", "")
            marker = "path not found during last sync; check move/rename"
            if marker not in prior:
                record["notes"] = (prior + " | " + marker).strip(" |")
        result.append(record)

    labels_path.parent.mkdir(parents=True, exist_ok=True)
    with labels_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(result)
    print(f"Image paths in manifest: {len(result)}")
    print(f"New images added for review: {new_count}")
    print(f"Manifest: {labels_path}")
    print("Existing source, license and attribute annotations were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
