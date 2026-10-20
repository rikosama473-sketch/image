#!/usr/bin/env python3
"""Split sprite sheets into uniformly sized transparent PNG crops with provenance."""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_slug(value: str, field: str = "identifier") -> str:
    raw = str(value).strip()
    if not raw or "/" in raw or "\\" in raw or "\n" in raw or "\r" in raw:
        raise ValueError(f"Invalid {field}: paths and line breaks are not allowed.")
    result = re.sub(r"[^a-zA-Z0-9_-]+", "-", raw).strip("-_").lower()
    if not result or result in {".", ".."}:
        raise ValueError(f"Invalid {field}: use letters, numbers, '-' or '_'.")
    return result


def parse_size(value: str, field: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*[xX,]\s*(\d+)\s*", value)
    if not match:
        raise argparse.ArgumentTypeError(f"{field} must look like 512x512.")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 1 or height < 1 or width > 8192 or height > 8192:
        raise argparse.ArgumentTypeError(f"{field} must be between 1 and 8192 pixels per side.")
    return width, height


def parse_color(value: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", text):
        raise argparse.ArgumentTypeError("Color must be #RRGGBB, for example #FFFFFF.")
    return tuple(int(text[pos:pos + 2], 16) for pos in (0, 2, 4))


def grid_boxes(image_size: tuple[int, int], cols: int, rows: int, prefix: str, category: str) -> list[dict[str, Any]]:
    width, height = image_size
    if cols < 1 or rows < 1 or cols > width or rows > height:
        raise ValueError(f"Grid {cols}x{rows} does not fit image dimensions {width}x{height}.")
    boxes = []
    for row in range(rows):
        top, bottom = row * height // rows, (row + 1) * height // rows
        for col in range(cols):
            left, right = col * width // cols, (col + 1) * width // cols
            index = row * cols + col + 1
            boxes.append({
                "id": f"{prefix}-{index:03d}", "category": category,
                "name": f"Cell {index}", "bbox": [left, top, right - left, bottom - top],
            })
    return boxes


def load_explicit_boxes(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read boxes JSON {path}: {exc}") from exc
    raw_assets = data.get("assets") if isinstance(data, dict) else data
    if not isinstance(raw_assets, list) or not raw_assets:
        raise ValueError("Boxes JSON must be a non-empty list or an object with an 'assets' list.")
    result = []
    for index, raw in enumerate(raw_assets, 1):
        if not isinstance(raw, dict) or not isinstance(raw.get("bbox"), list) or len(raw["bbox"]) != 4:
            raise ValueError(f"Asset entry {index} needs bbox: [x, y, width, height].")
        if any(isinstance(n, bool) or not isinstance(n, int) for n in raw["bbox"]):
            raise ValueError(f"Asset entry {index} bbox values must be integers.")
        result.append({
            "id": safe_slug(str(raw.get("id") or f"asset-{index:03d}"), "asset id"),
            "category": safe_slug(str(raw.get("category") or "misc"), "category"),
            "name": str(raw.get("name") or raw.get("id") or f"Asset {index}"),
            "bbox": raw["bbox"],
        })
    ids = [asset["id"] for asset in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Asset IDs must be unique after normalization.")
    return result


def validate_boxes(assets: list[dict[str, Any]], image_size: tuple[int, int]) -> None:
    width, height = image_size
    for asset in assets:
        x, y, box_width, box_height = asset["bbox"]
        if x < 0 or y < 0 or box_width < 1 or box_height < 1:
            raise ValueError(f"{asset['id']}: bbox must have non-negative origin and positive size.")
        if x + box_width > width or y + box_height > height:
            raise ValueError(f"{asset['id']}: bbox {asset['bbox']} exceeds image {width}x{height}.")


def remove_connected_key_color(image: Image.Image, key: tuple[int, int, int], tolerance: int) -> tuple[Image.Image, int]:
    """Remove only key-colored pixels connected to the crop border, preserving isolated white details."""
    if not 0 <= tolerance <= 255:
        raise ValueError("Key-color tolerance must be between 0 and 255.")
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    visited = bytearray(width * height)
    queue: deque[int] = deque()

    def matches(index: int) -> bool:
        r, g, b, alpha = pixels[index % width, index // width]
        return alpha > 0 and max(abs(r - key[0]), abs(g - key[1]), abs(b - key[2])) <= tolerance

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if not visited[index] and matches(index):
            visited[index] = 1
            queue.append(index)

    for x in range(width):
        seed(x, 0)
        if height > 1:
            seed(x, height - 1)
    for y in range(1, max(1, height - 1)):
        seed(0, y)
        if width > 1:
            seed(width - 1, y)

    removed = 0
    while queue:
        index = queue.popleft()
        x, y = index % width, index // width
        r, g, b, alpha = pixels[x, y]
        if alpha:
            pixels[x, y] = (r, g, b, 0)
            removed += 1
        if x > 0:
            seed(x - 1, y)
        if x + 1 < width:
            seed(x + 1, y)
        if y > 0:
            seed(x, y - 1)
        if y + 1 < height:
            seed(x, y + 1)
    return rgba, removed


def normalize_asset(
    image: Image.Image,
    canvas_size: tuple[int, int],
    key_color: tuple[int, int, int] | None = None,
    key_tolerance: int = 0,
    trim_alpha: bool = False,
) -> tuple[Image.Image, dict[str, Any]]:
    rgba = image.convert("RGBA")
    removed = 0
    if key_color is not None:
        rgba, removed = remove_connected_key_color(rgba, key_color, key_tolerance)
    alpha_bbox = rgba.getchannel("A").getbbox()
    if alpha_bbox is None:
        raise ValueError("Crop is completely transparent after background processing.")
    if trim_alpha:
        rgba = rgba.crop(alpha_bbox)
    fit_source_size = list(rgba.size)
    target_w, target_h = canvas_size
    scale = min(target_w / rgba.width, target_h / rgba.height)
    resized = rgba.resize(
        (max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    canvas.alpha_composite(resized, dest=((target_w - resized.width) // 2, (target_h - resized.height) // 2))
    alpha = canvas.getchannel("A")
    transparent_ratio = sum(1 for value in alpha.getdata() if value == 0) / (canvas.width * canvas.height)
    return canvas, {
        "crop_size_before_trim": list(image.size),
        "size_before_canvas_fit": fit_source_size,
        "canvas_size": list(canvas_size),
        "alpha_bbox_before_trim": list(alpha_bbox),
        "trimmed_alpha_bounds": bool(trim_alpha),
        "border_background_pixels_made_transparent": removed,
        "transparent_pixel_ratio": round(transparent_ratio, 6),
    }


def build_contact_sheet(assets: list[tuple[dict[str, Any], Image.Image]]) -> Image.Image:
    tile_w, tile_h = 192, 224
    cols = min(4, max(1, len(assets)))
    rows = (len(assets) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), (238, 240, 244))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (record, image) in enumerate(assets):
        col, row = index % cols, index // cols
        left, top = col * tile_w, row * tile_h
        for yy in range(top + 4, top + tile_h - 34, 12):
            for xx in range(left + 4, left + tile_w - 4, 12):
                color = (220, 223, 228) if ((xx // 12) + (yy // 12)) % 2 else (250, 250, 251)
                draw.rectangle((xx, yy, min(xx + 11, left + tile_w - 5), min(yy + 11, top + tile_h - 35)), fill=color)
        preview = image.copy()
        preview.thumbnail((tile_w - 20, tile_h - 48), Image.Resampling.LANCZOS)
        x = left + (tile_w - preview.width) // 2
        y = top + 4 + ((tile_h - 42) - preview.height) // 2
        sheet.paste(preview, (x, y), preview)
        draw.text((left + 6, top + tile_h - 30), f"{record['category']}/{record['id']}"[:30], fill=(30, 35, 45), font=font)
    return sheet


def run(
    input_path: Path, output_dir: Path, assets: list[dict[str, Any]],
    canvas_size: tuple[int, int], key_color: tuple[int, int, int] | None,
    key_tolerance: int, trim_alpha: bool, source_url: str | None,
    source_license: str | None, credit: str | None, overwrite: bool,
) -> Path:
    if not input_path.is_file():
        raise ValueError(f"Input image does not exist: {input_path}")
    input_bytes = input_path.read_bytes()
    source_sha = sha256_bytes(input_bytes)
    with Image.open(io.BytesIO(input_bytes)) as original:
        original.load()
        source_image = original.convert("RGBA")
    validate_boxes(assets, source_image.size)

    prepared = []
    target_paths = []
    for spec in assets:
        x, y, width, height = spec["bbox"]
        crop = source_image.crop((x, y, x + width, y + height))
        normalized, details = normalize_asset(crop, canvas_size, key_color, key_tolerance, trim_alpha)
        buffer = io.BytesIO()
        normalized.save(buffer, format="PNG", optimize=True)
        raw = buffer.getvalue()
        target_paths.append(output_dir / spec["category"] / f"{spec['id']}.png")
        prepared.append((spec, normalized, details, raw))

    manifest_path, contact_path = output_dir / "manifest.json", output_dir / "contact-sheet.png"
    collisions = [str(path) for path in [*target_paths, manifest_path, contact_path] if path.exists()]
    if collisions and not overwrite:
        raise FileExistsError("Refusing to overwrite existing output(s): " + ", ".join(collisions) + ". Use --overwrite to replace them.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_records, contact_records = [], []
    for spec, normalized, details, raw in prepared:
        destination = output_dir / spec["category"] / f"{spec['id']}.png"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        output_records.append({
            "id": spec["id"], "name": spec["name"], "category": spec["category"],
            "bbox_xywh": spec["bbox"], "output": destination.relative_to(output_dir).as_posix(),
            "sha256": sha256_bytes(raw), "dimensions": list(normalized.size), **details,
        })
        contact_records.append((spec, normalized))

    contact = build_contact_sheet(contact_records)
    buffer = io.BytesIO()
    contact.save(buffer, format="PNG", optimize=True)
    contact_bytes = buffer.getvalue()
    contact_path.write_bytes(contact_bytes)
    manifest = {
        "schema_version": 1, "tool": "scripts/split_sprite_sheet.py",
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(input_path), "sha256": source_sha, "dimensions": list(source_image.size),
            "url": source_url, "license": source_license, "credit": credit,
        },
        "processing": {
            "mode": "explicit_boxes_or_grid", "canvas_size": list(canvas_size),
            "background_key_color_rgb": list(key_color) if key_color is not None else None,
            "background_key_tolerance": key_tolerance if key_color is not None else None,
            "trim_alpha": trim_alpha, "semantic_layer_isolation_guaranteed": False,
            "note": "A cell is a hair/eye/accessory layer only if its source and crop coordinates actually isolate that part.",
        },
        "assets": output_records,
        "contact_sheet": {"file": "contact-sheet.png", "sha256": sha256_bytes(contact_bytes), "dimensions": list(contact.size)},
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source sprite sheet or grid image.")
    parser.add_argument("--output", required=True, type=Path, help="Output directory; originals are never modified.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--grid", help="Regular grid as COLUMNSxROWS, e.g. 5x4.")
    mode.add_argument("--boxes-json", type=Path, help="JSON file listing assets and bbox [x,y,width,height].")
    parser.add_argument("--canvas", default="512x512", help="Uniform output canvas, default 512x512.")
    parser.add_argument("--category", default="misc", help="Category for grid cells, e.g. hair or expressions.")
    parser.add_argument("--prefix", default="cell", help="ID prefix for grid cells.")
    parser.add_argument("--key-color", type=parse_color, help="Optional border-connected background color, e.g. #FFFFFF.")
    parser.add_argument("--key-tolerance", type=int, default=16, help="Maximum per-channel difference, from 0 to 255.")
    parser.add_argument("--trim-alpha", action="store_true", help="Trim transparent borders before fitting to the canvas.")
    parser.add_argument("--source-url", help="Optional canonical source URL for provenance.")
    parser.add_argument("--license", dest="source_license", help="Optional license string, such as CC-BY-4.0 or user-owned.")
    parser.add_argument("--credit", help="Optional creator/attribution text.")
    parser.add_argument("--overwrite", action="store_true", help="Replace colliding output files; disabled by default.")
    args = parser.parse_args()
    try:
        match = re.fullmatch(r"\s*(\d+)\s*[xX]\s*(\d+)\s*", args.grid) if args.grid else None
        if args.grid and not match:
            raise ValueError("--grid must look like 5x4.")
        canvas = parse_size(args.canvas, "--canvas")
        category, prefix = safe_slug(args.category, "category"), safe_slug(args.prefix, "prefix")
        if not 0 <= args.key_tolerance <= 255:
            raise ValueError("--key-tolerance must be between 0 and 255.")
        with Image.open(args.input) as image:
            size = image.size
        assets = grid_boxes(size, int(match.group(1)), int(match.group(2)), prefix, category) if match else load_explicit_boxes(args.boxes_json)
        manifest = run(args.input, args.output, assets, canvas, args.key_color, args.key_tolerance,
                       args.trim_alpha, args.source_url, args.source_license, args.credit, args.overwrite)
    except (OSError, ValueError, argparse.ArgumentTypeError, Image.DecompressionBombError) as exc:
        parser.error(str(exc))
    print(f"Created {len(assets)} assets plus contact sheet and manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
