#!/usr/bin/env python3
"""Audit local raster assets without modifying or deleting source files."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Iterable

from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "outputs", "runs", "checkpoints", "data/processed", "data/cache"}
REVIEW_FIELDS = (
    "visual_review",
    "license_review",
    "training_permission",
    "source_url",
    "author",
    "base_model_identifier",
    "lora_identifiers",
    "lora_weights_or_settings",
    "notes",
)

OUTPUT_FIELDS = [
    "path", "size_bytes", "width", "height", "mode", "has_alpha",
    "alpha_opaque_fraction", "sha256", "average_hash_8x8",
    "filename_origin_hint", *REVIEW_FIELDS,
]


def filename_origin_hint(path: str) -> str:
    name = Path(path).name
    if name.startswith("from-PixAI-"):
        return "PixAI filename clue; preserve exact name; verify account/origin and record model/LoRA separately"
    if name.lower().endswith(".png") and name[:-4].isdigit():
        return "numeric filename; origin unknown"
    return "unknown; review source"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def average_hash(image: Image.Image, size: int = 8) -> str:
    """Small perceptual hint only; equal hashes are not proof of duplicates."""
    gray = image.convert("L").resize((size, size), Image.Resampling.LANCZOS)
    values = list(gray.getdata())
    threshold = sum(values) / len(values)
    bits = 0
    for value in values:
        bits = (bits << 1) | int(value >= threshold)
    return f"{bits:0{(size * size + 3) // 4}x}"


def alpha_opaque_fraction(image: Image.Image) -> tuple[bool, str]:
    has_alpha = "A" in image.getbands() or "transparency" in image.info
    if not has_alpha:
        return False, ""
    alpha = image.convert("RGBA").getchannel("A")
    histogram = alpha.histogram()
    total = sum(histogram)
    opaque = histogram[255]
    return True, f"{opaque / total:.6f}" if total else ""


def should_skip(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    joined = "/".join(parts)
    for part in parts:
        if part in SKIP_DIRS:
            return True
    return joined.startswith("data/processed/") or joined.startswith("data/cache/")


def scan_images(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if should_skip(path, root):
            continue
        yield path


def read_existing_reviews(output_path: Path) -> dict[str, dict[str, str]]:
    if not output_path.exists():
        return {}
    try:
        with output_path.open("r", encoding="utf-8", newline="") as handle:
            return {row.get("path", ""): row for row in csv.DictReader(handle) if row.get("path")}
    except (OSError, csv.Error):
        return {}


def audit_one(path: Path, root: Path, old: dict[str, str]) -> dict[str, str]:
    relative = path.relative_to(root).as_posix()
    record: dict[str, str] = {
        "path": relative,
        "size_bytes": str(path.stat().st_size),
        "width": "",
        "height": "",
        "mode": "",
        "has_alpha": "false",
        "alpha_opaque_fraction": "",
        "sha256": sha256_file(path),
        "average_hash_8x8": "",
        "filename_origin_hint": filename_origin_hint(relative),
    }
    try:
        with Image.open(path) as image:
            image.load()
            record["width"] = str(image.width)
            record["height"] = str(image.height)
            record["mode"] = image.mode
            has_alpha, opaque_fraction = alpha_opaque_fraction(image)
            record["has_alpha"] = "true" if has_alpha else "false"
            record["alpha_opaque_fraction"] = opaque_fraction
            record["average_hash_8x8"] = average_hash(image)
    except Exception as exc:  # corrupted/unsupported images remain visible in the report
        record["mode"] = f"ERROR: {type(exc).__name__}: {exc}"

    for field in REVIEW_FIELDS:
        record[field] = old.get(field, "") or (
            "unreviewed" if field in {"visual_review", "license_review", "training_permission"} else ""
        )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository/local dataset root")
    parser.add_argument("--output", type=Path, default=Path("data/image-audit.csv"), help="CSV report path")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = read_existing_reviews(output)
    records = [audit_one(path, root, existing.get(path.relative_to(root).as_posix(), {})) for path in scan_images(root)]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    exact_hash_counts: dict[str, int] = {}
    for record in records:
        exact_hash_counts[record["sha256"]] = exact_hash_counts.get(record["sha256"], 0) + 1
    exact_dups = sum(count - 1 for count in exact_hash_counts.values() if count > 1)
    transparent = sum(record["has_alpha"] == "true" for record in records)
    errors = sum(record["mode"].startswith("ERROR:") for record in records)
    print(f"Images audited: {len(records)}")
    print(f"Files with an alpha channel: {transparent}")
    print(f"Exact duplicate files beyond the first copy: {exact_dups}")
    print(f"Unreadable/unsupported images: {errors}")
    print(f"Report: {output}")
    print("No image was moved, modified, or deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
