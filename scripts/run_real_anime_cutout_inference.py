#!/usr/bin/env python3
"""Run a real local anime background-removal inference and emit review artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps, __version__ as pillow_version


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("from-PixAI-2034984086876227343-0.png")


def fail(message: str) -> None:
    raise SystemExit("ERROR: " + message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Repository-relative source image.")
    parser.add_argument("--output", default="artifacts/real-anime-cutout", help="Output directory (relative to repository root).")
    parser.add_argument("--model", default="isnet-anime", choices=("isnet-anime", "birefnet-portrait"))
    return parser.parse_args()


def repo_relative_path(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        fail(f"{label} must be a repository-relative path without '..'.")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        fail(f"{label} resolves outside the repository.")
    return resolved


def alpha_metrics(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    total = image.width * image.height
    transparent = hist[0]
    near_transparent = sum(hist[1:9])
    low_alpha = sum(hist[9:65])
    transition = sum(hist[65:250])
    near_opaque = sum(hist[250:255])
    partial = sum(hist[1:255])
    opaque = hist[255]
    foreground = total - transparent
    bbox = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
    percent = lambda count: round(100 * count / total, 5)
    return {
        "width": image.width,
        "height": image.height,
        "pixels": total,
        "transparent_pixels": transparent,
        "partial_alpha_pixels": partial,
        "near_transparent_1_8_pixels": near_transparent,
        "low_alpha_9_64_pixels": low_alpha,
        "transition_alpha_65_249_pixels": transition,
        "near_opaque_250_254_pixels": near_opaque,
        "opaque_pixels": opaque,
        "transparent_percent": percent(transparent),
        "partial_alpha_percent": percent(partial),
        "near_transparent_1_8_percent": percent(near_transparent),
        "low_alpha_9_64_percent": percent(low_alpha),
        "transition_alpha_65_249_percent": percent(transition),
        "near_opaque_250_254_percent": percent(near_opaque),
        "opaque_percent": percent(opaque),
        "foreground_percent_alpha_gt_0": percent(foreground),
        "foreground_bbox_alpha_gt_8": list(bbox) if bbox else None,
        "alpha_is_non_binary": partial > 0,
        "alpha_has_transparency": transparent > 0,
    }


def checkerboard(image: Image.Image, cell: int = 24) -> Image.Image:
    """Flatten the alpha over a predictable checkerboard for edge inspection."""
    rgba = image.convert("RGBA")
    board = Image.new("RGBA", rgba.size, (232, 232, 232, 255))
    draw = ImageDraw.Draw(board)
    for y in range(0, rgba.height, cell):
        for x in range(0, rgba.width, cell):
            if ((x // cell) + (y // cell)) % 2:
                draw.rectangle(
                    (x, y, min(x + cell - 1, rgba.width - 1), min(y + cell - 1, rgba.height - 1)),
                    fill=(190, 190, 190, 255),
                )
    return Image.alpha_composite(board, rgba).convert("RGB")


def composite_on(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (*color, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def main() -> int:
    args = parse_args()
    input_path = repo_relative_path(args.input, "input")
    output_path = repo_relative_path(args.output, "output")
    if not input_path.is_file():
        fail("real source image not found: " + str(input_path.relative_to(ROOT)))
    source_bytes = input_path.read_bytes()
    if len(source_bytes) > 42 * 1024 * 1024:
        fail("source exceeds 42 MiB; choose an appropriately sized full illustration.")
    try:
        with Image.open(input_path) as opened:
            opened.verify()
        with Image.open(input_path) as opened:
            source = ImageOps.exif_transpose(opened).convert("RGBA")
            source.load()
    except Exception as exc:
        fail("cannot decode source image: " + type(exc).__name__ + ": " + str(exc))
    width, height = source.size
    if width < 64 or height < 64 or width * height > 20_000_000:
        fail(f"source dimensions {width}x{height} are outside the 64px–20MP test bounds.")
    if source.getchannel("A").getextrema() == (0, 0):
        fail("source image is fully transparent; choose a visible anime illustration.")

    try:
        from io import BytesIO
        import rembg
        from rembg import new_session, remove
    except ImportError:
        fail("install dependencies with: python -m pip install -r requirements-avatar-cutout.txt")

    normalized_buffer = BytesIO()
    source.save(normalized_buffer, format="PNG", optimize=True)
    normalized_source_bytes = normalized_buffer.getvalue()
    print(f"Running REAL inference: {input_path.relative_to(ROOT)} ({width}x{height}), model={args.model}", flush=True)
    # Reuse the same orientation-normalized PNG and edge decontamination as the local endpoint.
    session = new_session(args.model)
    output_bytes = remove(
        normalized_source_bytes,
        session=session,
        alpha_matting=False,
        post_process_mask=False,
        decontaminate=True,
        force_return_bytes=True,
    )
    if not isinstance(output_bytes, (bytes, bytearray)) or not output_bytes:
        fail("rembg returned no image bytes.")
    try:
        from io import BytesIO
        with Image.open(BytesIO(bytes(output_bytes))) as opened:
            opened.load()
            cutout = opened.convert("RGBA")
    except Exception as exc:
        fail("rembg output is not a readable image: " + type(exc).__name__ + ": " + str(exc))

    if cutout.size != source.size:
        fail(f"rembg changed dimensions from {source.size} to {cutout.size}; output rejected.")
    metrics = alpha_metrics(cutout)
    if metrics["transparent_pixels"] == 0:
        fail("real inference returned no transparent pixels.")
    foreground_count = metrics["pixels"] - metrics["transparent_pixels"]
    if foreground_count < max(100, int(metrics["pixels"] * 0.005)):
        fail("real inference retained too few foreground pixels; output likely empty.")
    if metrics["transparent_percent"] > 99.5:
        fail("real inference made almost the entire image transparent; output likely invalid.")

    output_path.mkdir(parents=True, exist_ok=True)
    source_output = output_path / "source.png"
    cutout_output = output_path / "cutout.png"
    mask_output = output_path / "alpha-mask.png"
    preview_output = output_path / "checkerboard-preview.jpg"
    dark_preview_output = output_path / "dark-background-preview.jpg"
    vivid_preview_output = output_path / "magenta-background-preview.jpg"
    white_preview_output = output_path / "white-background-preview.jpg"
    report_output = output_path / "metrics.json"
    source.save(source_output, format="PNG", optimize=True)
    cutout.save(cutout_output, format="PNG", optimize=True)
    cutout.getchannel("A").save(mask_output, format="PNG", optimize=True)
    checkerboard(cutout).save(preview_output, format="JPEG", quality=92, optimize=True)
    composite_on(cutout, (20, 20, 26)).save(dark_preview_output, format="JPEG", quality=92, optimize=True)
    composite_on(cutout, (235, 25, 125)).save(vivid_preview_output, format="JPEG", quality=92, optimize=True)
    composite_on(cutout, (255, 255, 255)).save(white_preview_output, format="JPEG", quality=92, optimize=True)

    report = {
        "schema_version": 1,
        "test_type": "real_model_inference",
        "review_status": "pending_human_visual_review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository_path": str(input_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(source_bytes),
            "bytes": len(source_bytes),
            "width": width,
            "height": height,
            "original_mode_after_normalization": "RGBA",
        },
        "model": args.model,
        "rembg_version": getattr(rembg, "__version__", "unknown"),
        "pillow_version": pillow_version,
        "python_version": platform.python_version(),
        "processing": {
            "alpha_matting": False,
            "post_process_mask": False,
            "decontaminate": True,
            "inference_real": True,
            "api_calls": 0,
        },
        "result": metrics,
        "artifacts": {
            "source": source_output.name,
            "cutout": cutout_output.name,
            "alpha_mask": mask_output.name,
            "checkerboard_preview": preview_output.name,
            "dark_background_preview": dark_preview_output.name,
            "magenta_background_preview": vivid_preview_output.name,
            "white_background_preview": white_preview_output.name,
        },
        "limitations": [
            "Automated metrics do not certify visual quality of fine hair, line art, halos, or shadow details.",
            "The cutout removes the background of the entire character; it does not split hair, eyes, clothing, and accessories into independent semantic pieces.",
            "Model weight licenses are separate from the rembg library license; review them before commercial use.",
        ],
    }
    report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS_REAL_INFERENCE",
        "report": str(report_output.relative_to(ROOT)),
        "previews": [str(path.relative_to(ROOT)) for path in (preview_output, dark_preview_output, vivid_preview_output, white_preview_output)],
        "result": metrics,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
