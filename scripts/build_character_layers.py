#!/usr/bin/env python3
"""Build reviewable character layers from the checked-in anime references.

This does not claim perfect semantic separation. Segmentation masks are candidates and
are explicitly marked for visual review; original references are never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

SEGMENTER_ID = "mattmdjaga/segformer_b2_clothes"
REMOVAL_MODEL = "u2net"
# Labels are resolved dynamically against model.config.id2label; these aliases are
# normalized so the code tolerates underscores, spaces, or hyphens in model labels.
LABEL_ALIASES = {
    "hair": {"hair"},
    "face": {"face", "skin"},
    "headwear": {"hat", "sunglasses"},
    "clothing": {
        "upper-clothes", "upper clothes", "skirt", "pants", "dress", "belt",
        "left-shoe", "right-shoe", "left-arm", "right-arm", "left-leg", "right-leg",
        "bag", "scarf",
    },
    "body_parts": {
        "upper-clothes", "upper clothes", "skirt", "pants", "dress", "belt",
        "left-shoe", "right-shoe", "left-arm", "right-arm", "left-leg", "right-leg",
        "bag", "scarf", "face", "skin", "hair", "hat", "sunglasses",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_label(value: str) -> str:
    value = str(value).lower().replace("_", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def labels_for_group(id2label: dict[Any, Any], group: str) -> set[int]:
    wanted = {normalize_label(item) for item in LABEL_ALIASES[group]}
    result = set()
    for raw_id, raw_label in id2label.items():
        label = normalize_label(raw_label)
        if label in wanted or label.replace("-", " ") in wanted:
            result.add(int(raw_id))
    return result


def mask_from_labels(label_map: Image.Image, ids: set[int]) -> Image.Image:
    """Return an L mask where the class-ID image matches any given class."""
    indexed = label_map.convert("L")
    lut = [255 if i in ids else 0 for i in range(256)]
    return indexed.point(lut)


def dilate(mask: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return mask.convert("L")
    size = radius * 2 + 1
    return mask.convert("L").filter(ImageFilter.MaxFilter(size))


def combine_masks(*masks: Image.Image) -> Image.Image:
    if not masks:
        raise ValueError("combine_masks requires at least one mask")
    result = masks[0].convert("L")
    for item in masks[1:]:
        result = ImageChops.lighter(result, item.convert("L"))
    return result


def intersect_masks(first: Image.Image, second: Image.Image) -> Image.Image:
    return ImageChops.multiply(first.convert("L"), second.convert("L"))


def subtract_mask(base: Image.Image, remove: Image.Image) -> Image.Image:
    return ImageChops.subtract(base.convert("L"), remove.convert("L"))


def alpha_ratio(mask: Image.Image) -> float:
    hist = mask.convert("L").histogram()
    total = sum(hist)
    return sum(hist[1:]) / total if total else 0.0


def edit_delta_mask(source: Image.Image, variant: Image.Image, threshold: int = 22) -> Image.Image:
    """Candidate delta mask for visual inspection, not a complete hair segmentation."""
    a = source.convert("RGB")
    b = variant.convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(a, b).convert("L")
    diff = diff.point(lambda px: 255 if px >= threshold else 0)
    width, height = diff.size
    # Keep only the broad upper-character region; this removes many clothing/pose
    # edits but cannot guarantee the mask only contains hair.
    upper = Image.new("L", (width, height), 0)
    ImageDraw.Draw(upper).rectangle(
        (int(width * 0.08), int(height * 0.01), int(width * 0.92), int(height * 0.48)),
        fill=255,
    )
    diff = intersect_masks(diff, upper)
    return dilate(diff, 3)


def as_rgba(image: Image.Image) -> Image.Image:
    return image.convert("RGBA")


def apply_alpha_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    if rgba.size != mask.size:
        mask = mask.resize(rgba.size, Image.Resampling.NEAREST)
    original_alpha = rgba.getchannel("A")
    effective = intersect_masks(original_alpha, mask)
    rgba.putalpha(effective)
    return rgba


def cutout_foreground(image_path: Path, session: Any) -> Image.Image:
    image = Image.open(image_path).convert("RGBA")
    # Reuse an existing meaningful alpha channel instead of degrading it by running
    # background removal twice.
    if alpha_ratio(image.getchannel("A")) < 0.985:
        return image
    from rembg import remove
    raw = image_path.read_bytes()
    result = remove(raw, session=session)
    return Image.open(io.BytesIO(result)).convert("RGBA")


def run_segmenter(image: Image.Image, processor: Any, model: Any, torch: Any) -> tuple[Image.Image, dict[int, str]]:
    import torch.nn.functional as F
    rgb = image.convert("RGB")
    inputs = processor(images=rgb, return_tensors="pt")
    with torch.inference_mode():
        outputs = model(**inputs)
        logits = F.interpolate(
            outputs.logits,
            size=(rgb.height, rgb.width),
            mode="bilinear",
            align_corners=False,
        )
        indices = logits.argmax(dim=1)[0].byte().cpu().numpy().tolist()
    # Build the indexed label image without importing numpy explicitly.
    indexed = Image.new("L", rgb.size)
    indexed.putdata([int(value) for row in indices for value in row])
    id2label = {int(key): str(value) for key, value in model.config.id2label.items()}
    return indexed, id2label


def load_models() -> tuple[Any, Any, Any, Any]:
    try:
        import torch
        from rembg import new_session
        from transformers import AutoImageProcessor, SegformerForSemanticSegmentation
    except ImportError as exc:
        raise RuntimeError(
            "Missing optional dependencies. Install requirements-character-layers.txt "
            "and the CPU PyTorch wheel; see docs/CHARACTER_LAYER_SEPARATION.md."
        ) from exc
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    processor = AutoImageProcessor.from_pretrained(SEGMENTER_ID)
    segmenter = SegformerForSemanticSegmentation.from_pretrained(SEGMENTER_ID)
    segmenter.eval()
    remover = new_session(REMOVAL_MODEL)
    return torch, processor, segmenter, remover


def make_contact_sheet(assets: list[tuple[str, Image.Image]], output: Path) -> None:
    cell_w, cell_h, label_h, cols = 260, 340, 34, 3
    rows = (len(assets) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), (42, 45, 52))
    draw = ImageDraw.Draw(sheet)
    for index, (label, layer) in enumerate(assets):
        x = (index % cols) * cell_w
        y = (index // cols) * (cell_h + label_h)
        tile = Image.new("RGBA", (cell_w, cell_h), (58, 62, 70, 255))
        checker = Image.new("RGB", (cell_w, cell_h), (72, 76, 84))
        cd = ImageDraw.Draw(checker)
        for yy in range(0, cell_h, 20):
            for xx in range(0, cell_w, 20):
                if (xx // 20 + yy // 20) % 2:
                    cd.rectangle((xx, yy, xx + 19, yy + 19), fill=(92, 96, 104))
        tile = Image.alpha_composite(checker.convert("RGBA"), tile)
        thumb = layer.copy()
        thumb.thumbnail((cell_w - 18, cell_h - 12), Image.Resampling.LANCZOS)
        tile.alpha_composite(thumb, ((cell_w - thumb.width) // 2, (cell_h - thumb.height) // 2))
        sheet.paste(tile.convert("RGB"), (x, y))
        draw.text((x + 8, y + cell_h + 8), label[:38], fill=(245, 245, 245))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG", optimize=True)


def parse_variant(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--variant requires ID=PATH")
    asset_id, raw_path = value.split("=", 1)
    asset_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", asset_id.strip()).strip("-_").lower()
    if not asset_id or not raw_path.strip():
        raise argparse.ArgumentTypeError("--variant requires non-empty ID and PATH")
    return asset_id, Path(raw_path.strip())


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    source_path = (root / args.source).resolve()
    if not source_path.is_file() or root not in source_path.parents:
        raise ValueError(f"Source image not found beneath repository root: {args.source}")
    variants: list[tuple[str, Path]] = []
    for asset_id, raw_path in args.variant:
        variant_path = (root / raw_path).resolve()
        if not variant_path.is_file() or root not in variant_path.parents:
            raise ValueError(f"Variant image not found beneath repository root: {raw_path}")
        variants.append((asset_id, variant_path))
    if not variants:
        raise ValueError("Provide at least one --variant ID=PATH to create hairstyle alternatives.")

    torch, processor, segmenter, remover = load_models()
    source = Image.open(source_path).convert("RGBA")
    source_cutout = cutout_foreground(source_path, remover)
    width, height = source.size
    if source_cutout.size != source.size:
        source_cutout = source_cutout.resize(source.size, Image.Resampling.LANCZOS)

    indexed, id2label = run_segmenter(source, processor, segmenter, torch)
    class_ids = {group: labels_for_group(id2label, group) for group in LABEL_ALIASES}
    hair_mask_raw = mask_from_labels(indexed, class_ids["hair"])
    face_mask_raw = mask_from_labels(indexed, class_ids["face"])
    headwear_mask_raw = mask_from_labels(indexed, class_ids["headwear"])
    clothing_mask_raw = mask_from_labels(indexed, class_ids["clothing"])

    foreground_alpha = source_cutout.getchannel("A")
    hair_mask = intersect_masks(dilate(hair_mask_raw, 4), foreground_alpha)
    face_mask = intersect_masks(dilate(face_mask_raw, 4), foreground_alpha)
    headwear_mask = intersect_masks(dilate(headwear_mask_raw, 3), foreground_alpha)
    head_mask = intersect_masks(dilate(combine_masks(hair_mask, face_mask, headwear_mask), 11), foreground_alpha)
    clothing_mask = intersect_masks(clothing_mask_raw, foreground_alpha)
    body_mask = subtract_mask(foreground_alpha, head_mask)

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, Any]] = []
    sheet_layers: list[tuple[str, Image.Image]] = []

    def save_layer(relative: str, image: Image.Image, role: str, method: str, status: str = "candidate_requires_visual_review", warning: str | None = None) -> None:
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format="PNG", optimize=True)
        assets.append({
            "path": path.relative_to(output).as_posix(),
            "role": role,
            "method": method,
            "dimensions": list(image.size),
            "sha256": sha256_file(path),
            "visible_pixel_ratio": round(alpha_ratio(image.getchannel("A")), 5),
            "status": status,
            "warning": warning,
        })
        sheet_layers.append((role + " / " + Path(relative).stem, image))

    save_layer("model/whole-character.png", source_cutout, "whole_character", "rembg u2net foreground cutout")
    save_layer("model/head-face-candidate.png", apply_alpha_mask(source_cutout, head_mask), "head_face_candidate", "SegFormer hair+face+headwear masks, dilated and clipped to foreground",
               warning="Candidate head mask: anime-domain accuracy is unvalidated; inspect hairline, ears, neck and accessories.")
    save_layer("model/body-without-head-candidate.png", apply_alpha_mask(source_cutout, body_mask), "body_without_head_candidate", "whole-character alpha minus dilated semantic head mask",
               warning="Candidate body layer may retain missed head pixels or remove neck/hair strands; inspect the join before compositing.")
    save_layer("model/face-candidate.png", apply_alpha_mask(source_cutout, face_mask), "face_candidate", "SegFormer face class",
               warning="Face parsing may omit eyes, eyebrows, ears, neck and stylized anime details.")
    save_layer("model/outfit-candidate.png", apply_alpha_mask(source_cutout, clothing_mask), "outfit_candidate", "SegFormer clothing/body accessory classes",
               warning="Class mask is designed for human photos and may omit anime line art, folds, jewelry or clothing pixels.")
    save_layer("hair/base-hair-candidate.png", apply_alpha_mask(source_cutout, hair_mask), "base_hair_candidate", "SegFormer Hair class",
               warning="Hair mask is a draft semantic extraction; compare against the source and repair edges by hand.")

    variant_metadata = []
    for asset_id, variant_path in variants:
        variant = Image.open(variant_path).convert("RGBA")
        if variant.size != source.size:
            variant = variant.resize(source.size, Image.Resampling.LANCZOS)
        variant_cutout = cutout_foreground(variant_path, remover)
        if variant_cutout.size != source.size:
            variant_cutout = variant_cutout.resize(source.size, Image.Resampling.LANCZOS)
        variant_indexed, variant_id2label = run_segmenter(variant, processor, segmenter, torch)
        variant_hair_ids = labels_for_group(variant_id2label, "hair")
        variant_semantic = mask_from_labels(variant_indexed, variant_hair_ids)
        variant_hair = intersect_masks(dilate(variant_semantic, 4), variant_cutout.getchannel("A"))
        method = "SegFormer Hair class clipped to rembg foreground"
        warning = "Review this isolated candidate; segmentation may miss wisps, ties, ribbons, and hair that overlaps the face."
        if alpha_ratio(variant_hair) < 0.006:
            # Fallback is deliberately labelled as a change-delta candidate, not a full
            # hair layer: identity/edit drift can also be present in the difference.
            delta_mask = edit_delta_mask(source, variant)
            variant_hair = intersect_masks(delta_mask, variant_cutout.getchannel("A"))
            method = "upper-region image-difference delta fallback"
            warning = "Fallback contains changed pixels in the upper character region, not guaranteed hair-only pixels; manual review is mandatory."
        output_layer = apply_alpha_mask(variant_cutout, variant_hair)
        path = f"hair/variants/{asset_id}.png"
        save_layer(path, output_layer, f"hair_variant_{asset_id}", method, warning=warning)

        delta_mask = intersect_masks(edit_delta_mask(source, variant), variant_cutout.getchannel("A"))
        delta_layer = apply_alpha_mask(variant_cutout, delta_mask)
        save_layer(
            f"hair/edit-delta/{asset_id}-delta-candidate.png",
            delta_layer,
            f"edit_delta_{asset_id}",
            "pixel difference restricted to upper 48% of canvas",
            warning="This is a diagnostic patch, not the full hairstyle; it can include unintended face/background changes.",
        )
        variant_metadata.append({
            "id": asset_id,
            "source_path": variant_path.relative_to(root).as_posix(),
            "source_sha256": sha256_file(variant_path),
        })

    # Include render variants in a source-vs-style overview while preserving exact
    # full-body renders as their own source files in the original repository.
    manifest = {
        "schema_version": 1,
        "character_id": args.character,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": source_path.relative_to(root).as_posix(),
            "sha256": sha256_file(source_path),
            "dimensions": [width, height],
        },
        "models": {
            "foreground_removal": REMOVAL_MODEL,
            "semantic_segmenter": SEGMENTER_ID,
            "semantic_segmenter_labels": {str(key): value for key, value in id2label.items()},
            "class_ids_used": {key: sorted(value) for key, value in class_ids.items()},
        },
        "alignment": "Every layer preserves the source image canvas size and coordinates.",
        "status": "generated_candidates_pending_visual_review",
        "quality_note": "The semantic model was trained on human clothing imagery, not guaranteed anime artwork. No asset in this pack is marked production-approved.",
        "variants": variant_metadata,
        "assets": assets,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_contact_sheet(sheet_layers, output / "contact-sheet.png")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--character", default="pibara")
    parser.add_argument("--source", required=True, help="repository-relative source image")
    parser.add_argument("--variant", action="append", default=[], type=parse_variant, help="repeat ID=PATH for hairstyle variants")
    parser.add_argument("--output", type=Path, required=True, help="output directory, normally under generated/character-layers/")
    args = parser.parse_args()
    try:
        manifest = build(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "output": str(args.output),
        "asset_count": len(manifest["assets"]),
        "status": manifest["status"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
