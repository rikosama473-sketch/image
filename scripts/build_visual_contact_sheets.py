#!/usr/bin/env python3
"""Build visual contact sheets and an exact-duplicate report for IMAGE's local image catalog.

Run from the repository root:
    python scripts/build_visual_contact_sheets.py
Requires Pillow: python -m pip install Pillow
This script reads local files only. It does not download references or infer rights.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "tools/avatar-maker/assets/image-library.json"
DEFAULT_OUTPUT = ROOT / "generated/visual-reference-contact-sheets"


def safe_asset_path(relative: str) -> Path | None:
    raw = Path(relative)
    if raw.is_absolute() or ".." in raw.parts:
        return None
    path = (ROOT / raw).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return None
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if candidate.is_file():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    canvas = Image.new("RGB", size, (235, 238, 243))
    draw = ImageDraw.Draw(canvas)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(x + cell - 1, size[0]), min(y + cell - 1, size[1])), fill=(205, 212, 223))
    return canvas


def render_thumbnail(path: Path, size: tuple[int, int]) -> tuple[Image.Image, tuple[int, int], str, str]:
    with Image.open(path) as original:
        original.load()
        dims = original.size
        image_format = str(original.format or "unknown")
        full_rgba = original.convert("RGBA")
        # Hash the visible artwork on a neutral white background so alpha-only
        # differences do not dominate the near-duplicate check.
        flattened = Image.new("RGBA", full_rgba.size, (255, 255, 255, 255))
        flattened.alpha_composite(full_rgba)
        gray = ImageOps.grayscale(flattened).resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
        bits = 0
        for y in range(8):
            for x in range(8):
                if pixels[y * 9 + x] > pixels[y * 9 + x + 1]:
                    bits |= 1 << (y * 8 + x)
        difference_hash = f"{bits:016x}"
        rgba = full_rgba.copy()
        rgba.thumbnail(size, Image.Resampling.LANCZOS)
        background = checkerboard(size)
        x = (size[0] - rgba.width) // 2
        y = (size[1] - rgba.height) // 2
        background.paste(rgba, (x, y), rgba.getchannel("A"))
    return background, dims, image_format, difference_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-sheet", type=int, default=48)
    args = parser.parse_args()
    if args.per_sheet < 1 or args.per_sheet > 120:
        raise SystemExit("--per-sheet must be between 1 and 120")
    catalog_path = args.catalog if args.catalog.is_absolute() else ROOT / args.catalog
    output = args.output if args.output.is_absolute() else ROOT / args.output
    data: dict[str, Any] = json.loads(catalog_path.read_text(encoding="utf-8"))
    assets = data.get("assets", [])
    if not isinstance(assets, list):
        raise SystemExit("Catalog field 'assets' must be an array.")
    output.mkdir(parents=True, exist_ok=True)

    columns = 6
    rows = math.ceil(args.per_sheet / columns)
    cell_w, cell_h = 220, 252
    thumb_w, thumb_h = 204, 205
    title_font, meta_font = load_font(12), load_font(10)
    rows_out: list[dict[str, Any]] = []
    exact_hashes: dict[str, list[str]] = defaultdict(list)
    duplicates: dict[str, list[dict[str, str]]] = {}
    errors: list[dict[str, str]] = []
    prepared: list[dict[str, Any]] = []

    for index, asset in enumerate(assets, start=1):
        asset_id = str(asset.get("id") or f"asset-{index:04d}")
        relative = str(asset.get("path") or "")
        path = safe_asset_path(relative) if relative else None
        record: dict[str, Any] = {
            "id": asset_id,
            "catalog_id": str(asset.get("catalog_id") or ""),
            "label": str(asset.get("label") or asset_id),
            "path": relative,
            "visual_review": str(asset.get("visual_review") or "unreviewed"),
            "exists": bool(path and path.is_file()),
            "width": None,
            "height": None,
            "format": None,
            "sha256": None,
            "dhash64": None,
            "exact_duplicate_of": None,
            "error": "",
        }
        thumb = None
        if not path or not path.is_file():
            record["error"] = "missing_or_unsafe_path"
        else:
            try:
                record["sha256"] = sha256_file(path)
                exact_hashes[record["sha256"]].append(asset_id)
                thumb, dimensions, image_format, difference_hash = render_thumbnail(path, (thumb_w, thumb_h))
                record["width"], record["height"] = dimensions
                record["format"] = image_format
                record["dhash64"] = difference_hash
            except Exception as exc:  # report one broken image; continue the catalogue
                record["error"] = f"{type(exc).__name__}: {exc}"
        if record["error"]:
            errors.append({"id": asset_id, "path": relative, "error": record["error"]})
        prepared.append({"record": record, "thumbnail": thumb})
        rows_out.append(record)

    first_ids: dict[str, str] = {}
    for row in rows_out:
        digest = row.get("sha256")
        if not digest:
            continue
        if digest in first_ids:
            row["exact_duplicate_of"] = first_ids[digest]
            duplicates.setdefault(digest, [{"id": first_ids[digest], "path": next((r["path"] for r in rows_out if r["id"] == first_ids[digest]), "")}]).append({"id": row["id"], "path": row["path"]})
        else:
            first_ids[digest] = row["id"]

    # Perceptual dHash catches candidates that differ slightly in encoding, crop,
    # or a small region. It is only a review queue, never an auto-delete decision.
    near_duplicate_candidates: list[dict[str, Any]] = []
    hashable = [row for row in rows_out if row.get("dhash64") and row.get("sha256")]
    for left_index, left in enumerate(hashable):
        left_hash = int(str(left["dhash64"]), 16)
        for right in hashable[left_index + 1:]:
            if left.get("sha256") == right.get("sha256"):
                continue
            distance = (left_hash ^ int(str(right["dhash64"]), 16)).bit_count()
            if distance <= 3:
                near_duplicate_candidates.append({
                    "hamming_distance": distance,
                    "id_a": left["id"],
                    "path_a": left["path"],
                    "id_b": right["id"],
                    "path_b": right["path"],
                    "review_status": "candidate_requires_visual_confirmation",
                })
    near_duplicate_candidates.sort(key=lambda item: (item["hamming_distance"], item["path_a"], item["path_b"]))
    (output / "near-duplicates-candidates.json").write_text(
        json.dumps(near_duplicate_candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for start in range(0, len(prepared), args.per_sheet):
        group = prepared[start:start + args.per_sheet]
        sheet_index = start // args.per_sheet + 1
        actual_rows = math.ceil(len(group) / columns)
        sheet = Image.new("RGB", (columns * cell_w, actual_rows * cell_h), (13, 22, 37))
        draw = ImageDraw.Draw(sheet)
        for offset, item in enumerate(group):
            col, row_no = offset % columns, offset // columns
            x, y = col * cell_w, row_no * cell_h
            record = item["record"]
            draw.rounded_rectangle((x + 5, y + 5, x + cell_w - 5, y + cell_h - 5), radius=8, fill=(22, 34, 53), outline=(60, 79, 108), width=1)
            thumb = item["thumbnail"]
            if thumb is not None:
                sheet.paste(thumb, (x + 8, y + 8))
            else:
                draw.text((x + 17, y + 85), "NO IMAGE", font=title_font, fill=(255, 168, 183))
            label = str(record["label"]).replace("\n", " ")
            if len(label) > 29:
                label = label[:26] + "..."
            draw.text((x + 9, y + 218), f'{record["id"]} · {label}', font=title_font, fill=(244, 247, 255))
            path_label = str(record["path"])
            if len(path_label) > 32:
                path_label = "…" + path_label[-31:]
            draw.text((x + 9, y + 236), path_label, font=meta_font, fill=(165, 184, 210))
        target = output / f"contact-sheet-{sheet_index:02d}.jpg"
        sheet.save(target, quality=88, optimize=True)
        print(f"Created {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")

    csv_path = output / "asset-manifest.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0].keys()) if rows_out else ["id", "path"])
        writer.writeheader()
        writer.writerows(rows_out)
    duplicate_groups = [group for group in duplicates.values() if len(group) > 1]
    (output / "exact-duplicates.json").write_text(json.dumps(duplicate_groups, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "schema_version": 1,
        "source_catalog": str(catalog_path.relative_to(ROOT)) if catalog_path.is_relative_to(ROOT) else str(catalog_path),
        "assets_indexed": len(assets),
        "images_readable": sum(1 for x in rows_out if x["width"] and x["height"]),
        "missing_or_unreadable": len(errors),
        "exact_duplicate_groups": len(duplicate_groups),
        "exact_duplicate_extra_files": sum(len(group) - 1 for group in duplicate_groups),
        "near_duplicate_candidate_pairs": len(near_duplicate_candidates),
        "contact_sheets": math.ceil(len(prepared) / args.per_sheet),
        "review_policy": "Contact sheets support human visual review; metadata and filenames do not establish visual class, authorship, rights, or training permission.",
        "errors": errors,
    }
    (output / "contact-sheet-index.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("assets_indexed", "images_readable", "missing_or_unreadable", "exact_duplicate_groups", "near_duplicate_candidate_pairs", "contact_sheets")}, indent=2))


if __name__ == "__main__":
    main()
