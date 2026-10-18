#!/usr/bin/env python3
"""Extract generation metadata embedded in local images without changing them.

The report helps trace prompts, base checkpoints and LoRAs. Blank fields mean
metadata was absent or could not be parsed confidently; never guess from names.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from PIL import ExifTags, Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "outputs", "runs",
    "checkpoints", "models", "node_modules", "data/cache", "data/processed",
    "data/asset-cache",
}
FIELDS = [
    "path", "format", "width", "height", "metadata_present", "metadata_keys",
    "prompt", "negative_prompt", "base_model_identifier", "base_model_hash",
    "lora_identifiers", "lora_weights_or_settings", "sampler", "steps",
    "cfg_scale", "seed", "metadata_sha256", "parse_notes",
]
BASE_MODEL_KEYS = {
    "model", "model_name", "model_id", "base_model", "base_model_name",
    "base_model_identifier", "checkpoint", "checkpoint_name", "ckpt_name",
    "ckpt", "model_identifier", "model_path",
}
BASE_HASH_KEYS = {"model_hash", "base_model_hash", "checkpoint_hash", "ckpt_hash"}
PROMPT_KEYS = {"prompt", "positive_prompt", "prompt_text", "positive", "caption", "text"}
NEGATIVE_KEYS = {"negative_prompt", "negative_prompt_text", "negative", "uc"}
ALIASES = {
    "sampler": {"sampler", "sampler_name", "sampling_method"},
    "steps": {"steps", "num_steps", "sampling_steps"},
    "cfg_scale": {"cfg", "cfg_scale", "guidance_scale", "guidance"},
    "seed": {"seed", "random_seed"},
}
PARAM_RE = re.compile(
    r"\b(Steps|Sampler|CFG scale|CFG|Seed|Model hash|Model|Denoising strength)\s*:\s*([^,\n]+)",
    re.IGNORECASE,
)
LORA_TAG_RE = re.compile(r"<lora:([^:>]+):([^>]+)>", re.IGNORECASE)


def _norm_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _as_text(value: Any) -> str:
    safe = _json_safe(value)
    if isinstance(safe, str):
        return safe.strip()
    if isinstance(safe, (dict, list)):
        return json.dumps(safe, ensure_ascii=False, sort_keys=True)
    return "" if safe is None else str(safe)


def _expand_json_text(value: str) -> Any | None:
    stripped = value.strip()
    if not stripped or stripped[0] not in "{[":
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, (dict, list)) else None


def flatten_metadata(data: Any, prefix: str = "") -> list[tuple[str, str]]:
    """Flatten nested metadata and JSON-encoded workflow values into key/value pairs."""
    result: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            child_key = f"{prefix}.{key}" if prefix else str(key)
            result.extend(flatten_metadata(value, child_key))
        return result
    if isinstance(data, (list, tuple)):
        for index, value in enumerate(data):
            result.extend(flatten_metadata(value, f"{prefix}[{index}]"))
        return result
    text = _as_text(data)
    nested = _expand_json_text(text)
    if nested is not None:
        result.extend(flatten_metadata(nested, prefix))
    elif text:
        result.append((prefix, text))
    return result


def parse_parameters(text: str) -> dict[str, str]:
    """Read common Automatic1111/Forge-style parameter blocks when present."""
    result: dict[str, str] = {}
    negative_match = re.search(
        r"Negative prompt:\s*(.*?)(?=\n\s*(?:Steps|Sampler|CFG scale|CFG|Seed|Model|Model hash)\s*:|$)",
        text, re.IGNORECASE | re.DOTALL,
    )
    if negative_match:
        result["negative_prompt"] = negative_match.group(1).strip()
    positive = text[:negative_match.start()] if negative_match else text
    if not negative_match:
        config_match = re.search(
            r"\n\s*(?:Steps|Sampler|CFG scale|CFG|Seed|Model|Model hash)\s*:",
            text, re.IGNORECASE,
        )
        if config_match:
            positive = text[:config_match.start()]
    if positive.strip():
        result["prompt"] = positive.strip()
    for match in PARAM_RE.finditer(text):
        key, value = match.group(1).lower(), match.group(2).strip()
        if key == "model":
            result.setdefault("base_model_identifier", value)
        elif key == "model hash":
            result.setdefault("base_model_hash", value)
        elif key == "sampler":
            result.setdefault("sampler", value)
        elif key in {"cfg", "cfg scale"}:
            result.setdefault("cfg_scale", value)
        elif key == "steps":
            result.setdefault("steps", value)
        elif key == "seed":
            result.setdefault("seed", value)
    loras = [f"{m.group(1).strip()}@{m.group(2).strip()}" for m in LORA_TAG_RE.finditer(text)]
    if loras:
        result["lora_identifiers"] = "; ".join(dict.fromkeys(loras))
        result["lora_weights_or_settings"] = "; ".join(dict.fromkeys(
            f"{m.group(1).strip()}={m.group(2).strip()}" for m in LORA_TAG_RE.finditer(text)
        ))
    return result


def _pick(flat: list[tuple[str, str]], aliases: set[str]) -> str:
    for key, value in flat:
        leaf = key.rsplit(".", 1)[-1].split("[", 1)[0]
        if _norm_key(leaf) in aliases and value.strip():
            return value.strip()
    return ""


def _metadata_for_image(image: Image.Image) -> dict[str, Any]:
    info = dict(image.info)
    try:
        for tag, value in image.getexif().items():
            info.setdefault(f"EXIF:{ExifTags.TAGS.get(tag, str(tag))}", _json_safe(value))
    except Exception:
        pass
    return _json_safe(info)


def extract_one(path: Path, root: Path) -> dict[str, str]:
    row = {field: "" for field in FIELDS}
    row["path"] = path.relative_to(root).as_posix()
    row["metadata_present"] = "false"
    row["parse_notes"] = "No embedded generation metadata found."
    try:
        with Image.open(path) as image:
            row["format"] = image.format or ""
            row["width"] = str(image.width)
            row["height"] = str(image.height)
            metadata = _metadata_for_image(image)
    except Exception as exc:
        row["parse_notes"] = f"Image read error: {type(exc).__name__}: {exc}"
        return row

    generation_words = ("prompt", "model", "lora", "adapter", "parameter", "workflow", "seed", "sampler", "steps", "cfg")
    if any(any(word in _norm_key(key) for word in generation_words) for key in metadata):
        row["metadata_present"] = "true"
    row["metadata_keys"] = "; ".join(sorted(str(key) for key in metadata))
    canonical = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    row["metadata_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    flat = flatten_metadata(metadata)

    row["prompt"] = _pick(flat, PROMPT_KEYS)
    row["negative_prompt"] = _pick(flat, NEGATIVE_KEYS)
    row["base_model_identifier"] = _pick(flat, BASE_MODEL_KEYS)
    row["base_model_hash"] = _pick(flat, BASE_HASH_KEYS)
    for field, aliases in ALIASES.items():
        row[field] = _pick(flat, aliases)

    lora_entries: list[str] = []
    for key, value in flat:
        norm = _norm_key(key)
        if "lora" in norm or "adapter" in norm:
            if value and value not in lora_entries:
                lora_entries.append(f"{key}={value}")
        parsed = parse_parameters(value)
        for field, parsed_value in parsed.items():
            if not row.get(field):
                row[field] = parsed_value
    if lora_entries:
        identifiers = lora_entries + ([row["lora_identifiers"]] if row["lora_identifiers"] else [])
        row["lora_identifiers"] = "; ".join(dict.fromkeys(identifiers))
    weight_entries = [
        f"{key}={value}" for key, value in flat
        if value and any(token in _norm_key(key) for token in ("lora_weight", "lora_strength", "adapter_weight", "strength_model", "strength_clip"))
    ]
    if weight_entries:
        prior_weights = [row["lora_weights_or_settings"]] if row["lora_weights_or_settings"] else []
        row["lora_weights_or_settings"] = "; ".join(dict.fromkeys(prior_weights + weight_entries))
    if row["metadata_present"] == "true":
        row["parse_notes"] = "Embedded generation-like metadata found; review extracted values manually."
    elif metadata:
        row["parse_notes"] = "Image metadata exists, but no obvious generation fields were detected."
    return row


def should_skip(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    if any(part in SKIP_DIRS or part.startswith(".") for part in parts):
        return True
    relative = path.relative_to(root).as_posix()
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in ("data/cache", "data/processed", "data/asset-cache"))


def scan_images(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and not should_skip(path, root):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository/local collection root")
    parser.add_argument(
        "--output", type=Path, default=Path("data/cache/generation-metadata.csv"),
        help="Local CSV destination; default stays inside ignored data/cache/",
    )
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    output = args.output.expanduser()
    output = output.resolve() if output.is_absolute() else root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [extract_one(path, root) for path in scan_images(root)]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Images scanned: {len(rows)}")
    print(f"Images with generation-like metadata: {sum(r['metadata_present'] == 'true' for r in rows)}")
    print(f"Base model identified in metadata: {sum(bool(r['base_model_identifier']) for r in rows)}")
    print(f"LoRA/adapter field found in metadata: {sum(bool(r['lora_identifiers']) for r in rows)}")
    print(f"Unreadable images: {sum(r['parse_notes'].startswith('Image read error:') for r in rows)}")
    print(f"Report: {output}")
    print("Original images were not modified. Review the CSV; blank fields are not guessed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
