#!/usr/bin/env python3
"""Crop a spritesheet grid into uniform, independently saved PNG assets.

Coordinates are pixel coordinates. This tool crops rectangles; it does not perform
semantic AI segmentation. A hair crop containing face/body pixels remains mixed.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
DEFAULT_LAYERS = {"body", "hair", "eyes", "clothing", "accessories", "expressions", "other"}


def positive_int(value: Any, label: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} debe ser un entero.") from exc
    if number <= 0:
        raise ValueError(f"{label} debe ser mayor que cero.")
    return number


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer la configuración {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise ValueError("La raíz de grid.json debe ser un objeto JSON.")
    return config


def resolve_grid(image: Image.Image, config: dict[str, Any]) -> tuple[int, int, int, int, int, int, int, int]:
    grid = config.get("grid", {})
    if not isinstance(grid, dict):
        raise ValueError("'grid' debe ser un objeto.")
    rows = positive_int(grid.get("rows"), "grid.rows")
    columns = positive_int(grid.get("columns"), "grid.columns")
    margin_x = int(grid.get("margin_x", 0))
    margin_y = int(grid.get("margin_y", 0))
    gap_x = int(grid.get("gap_x", 0))
    gap_y = int(grid.get("gap_y", 0))
    if min(margin_x, margin_y, gap_x, gap_y) < 0:
        raise ValueError("Márgenes y separaciones no pueden ser negativos.")

    usable_width = image.width - 2 * margin_x - (columns - 1) * gap_x
    usable_height = image.height - 2 * margin_y - (rows - 1) * gap_y
    if usable_width <= 0 or usable_height <= 0:
        raise ValueError("La grilla no cabe dentro de la imagen.")
    cell_width = positive_int(grid.get("cell_width", usable_width // columns), "grid.cell_width")
    cell_height = positive_int(grid.get("cell_height", usable_height // rows), "grid.cell_height")
    required_width = 2 * margin_x + columns * cell_width + (columns - 1) * gap_x
    required_height = 2 * margin_y + rows * cell_height + (rows - 1) * gap_y
    if required_width > image.width or required_height > image.height:
        raise ValueError(
            f"Grilla fuera de la imagen {image.width}x{image.height}; "
            f"necesita al menos {required_width}x{required_height}."
        )
    return rows, columns, cell_width, cell_height, margin_x, margin_y, gap_x, gap_y


def cell_box(row: int, column: int, cell_width: int, cell_height: int,
             margin_x: int, margin_y: int, gap_x: int, gap_y: int) -> tuple[int, int, int, int]:
    x = margin_x + (column - 1) * (cell_width + gap_x)
    y = margin_y + (row - 1) * (cell_height + gap_y)
    return x, y, x + cell_width, y + cell_height


def validate_layer(layer: Any) -> str:
    if not isinstance(layer, str) or not layer.strip():
        raise ValueError("Cada elemento necesita un nombre de capa no vacío.")
    name = layer.strip().lower().replace(" ", "_")
    if name in {".", ".."} or "/" in name or "\\" in name:
        raise ValueError(f"Nombre de capa no válido: {layer!r}")
    return name


def entries_from_config(config: dict[str, Any], rows: int, columns: int) -> list[dict[str, Any]]:
    # Cells and regions are two alternative mapping modes; reject ambiguous configs.
    if config.get("cells") is not None and config.get("regions") is not None:
        raise ValueError("Usa 'cells' o 'regions', pero no ambos a la vez.")
    entries = config.get("cells")
    if entries is None:
        # Region mode permits a different local rectangle inside a given cell.
        entries = config.get("regions")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Configura una lista no vacía 'cells' o 'regions'.")
    normalized: list[dict[str, Any]] = []
    seen_targets: set[tuple[int, int, str]] = set()
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Elemento {index} debe ser un objeto.")
        row = positive_int(item.get("row"), f"elemento {index}.row")
        column = positive_int(item.get("column"), f"elemento {index}.column")
        if row > rows or column > columns:
            raise ValueError(f"Elemento {index}: fila/columna fuera de la grilla.")
        layer = validate_layer(item.get("layer"))
        target = (row, column, layer)
        if target in seen_targets:
            raise ValueError(f"Asignación duplicada para fila {row}, columna {column}, capa {layer!r}.")
        seen_targets.add(target)
        bbox = item.get("bbox")
        if bbox is not None:
            if not isinstance(bbox, list) or len(bbox) != 4:
                raise ValueError(f"Elemento {index}.bbox debe ser [x, y, ancho, alto].")
            if any(isinstance(v, bool) or not isinstance(v, int) for v in bbox):
                raise ValueError(f"Elemento {index}.bbox requiere cuatro enteros.")
            x, y, width, height = bbox
            if min(x, y) < 0 or min(width, height) <= 0:
                raise ValueError(f"Elemento {index}.bbox contiene valores no válidos.")
            bbox = [x, y, width, height]
        normalized.append({"row": row, "column": column, "layer": layer, "bbox": bbox})
    return normalized


def fit_to_canvas(crop: Image.Image, size: tuple[int, int], resample: Image.Resampling) -> Image.Image:
    """Scale up or down proportionally, then center on a transparent fixed-size canvas."""
    crop = crop.convert("RGBA")
    target_w, target_h = size
    scale = min(target_w / crop.width, target_h / crop.height)
    scaled_size = (
        max(1, min(target_w, round(crop.width * scale))),
        max(1, min(target_h, round(crop.height * scale))),
    )
    if crop.size != scaled_size:
        crop = crop.resize(scaled_size, resample=resample)
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((target_w - crop.width) // 2, (target_h - crop.height) // 2))
    return canvas


def process(input_path: Path, config_path: Path, output_dir: Path) -> dict[str, Any]:
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("La imagen de entrada debe ser PNG, JPEG, WebP, BMP, TIFF o TIF.")
    config = load_config(config_path)
    try:
        with Image.open(input_path) as opened:
            source = ImageOps.exif_transpose(opened).convert("RGBA")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"No se pudo abrir la imagen {input_path}: {exc}") from exc

    rows, columns, cw, ch, mx, my, gx, gy = resolve_grid(source, config)
    entries = entries_from_config(config, rows, columns)
    output_config = config.get("output", {})
    if not isinstance(output_config, dict):
        raise ValueError("'output' debe ser un objeto.")
    out_w = positive_int(output_config.get("width", 512), "output.width")
    out_h = positive_int(output_config.get("height", 512), "output.height")
    resample_name = str(output_config.get("resample", "lanczos")).lower()
    resampling = {
        "nearest": Image.Resampling.NEAREST,
        "bilinear": Image.Resampling.BILINEAR,
        "bicubic": Image.Resampling.BICUBIC,
        "lanczos": Image.Resampling.LANCZOS,
    }
    if resample_name not in resampling:
        raise ValueError("output.resample debe ser nearest, bilinear, bicubic o lanczos.")
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "source": str(input_path),
        "source_dimensions": list(source.size),
        "grid": {"rows": rows, "columns": columns, "cell_width": cw, "cell_height": ch,
                 "margin_x": mx, "margin_y": my, "gap_x": gx, "gap_y": gy},
        "output_dimensions": [out_w, out_h],
        "note": "Recorte rectangular por coordenadas; no equivale a segmentación semántica.",
        "assets": [],
        "errors": [],
    }
    for item in entries:
        row, column, layer = item["row"], item["column"], item["layer"]
        x1, y1, x2, y2 = cell_box(row, column, cw, ch, mx, my, gx, gy)
        if item["bbox"] is not None:
            bx, by, bw, bh = item["bbox"]
            if bx + bw > (x2 - x1) or by + bh > (y2 - y1):
                manifest["errors"].append(
                    {"row": row, "column": column, "layer": layer,
                     "error": "bbox local excede el tamaño de la celda"}
                )
                continue
            x1, y1, x2, y2 = x1 + bx, y1 + by, x1 + bx + bw, y1 + by + bh

        cropped = source.crop((x1, y1, x2, y2))
        if cropped.getchannel("A").getbbox() is None:
            manifest["errors"].append(
                {"row": row, "column": column, "layer": layer, "error": "recorte completamente transparente"}
            )
            continue
        final_image = fit_to_canvas(cropped, (out_w, out_h), resampling[resample_name])
        folder = output_dir / layer
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"r{row:02d}_c{column:02d}_{layer}.png"
        destination = folder / filename
        final_image.save(destination, format="PNG", optimize=True)
        manifest["assets"].append({
            "layer": layer, "row": row, "column": column,
            "source_bbox_xyxy": [x1, y1, x2, y2],
            "output": destination.relative_to(output_dir).as_posix(),
            "size": [out_w, out_h],
            "mode": "RGBA",
            "alpha_bbox": list(final_image.getchannel("A").getbbox()) if final_image.getchannel("A").getbbox() else None,
        })

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Recorta una grilla de sprites a PNG uniformes.")
    parser.add_argument("--input", type=Path, default=Path("input/spritesheet.png"))
    parser.add_argument("--config", type=Path, default=Path("config/grid.json"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()

    try:
        manifest = process(args.input, args.config, args.output)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Assets guardados: {len(manifest['assets'])}")
    print(f"Errores de recorte: {len(manifest['errors'])}")
    print(f"Manifiesto: {args.output / 'manifest.json'}")
    return 1 if manifest["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
