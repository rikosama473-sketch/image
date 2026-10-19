#!/usr/bin/env python3
"""Safe, offline, read-only IMAGE collection and hardware diagnostic.

This tool never loads a generative model, reads prompts into a report, modifies
source images, downloads files, or sends data over the network.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import time
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

APP_VERSION = "1.0.0"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    "models", "outputs", "runs", "checkpoints", "build", "dist",
    "cache", "processed", "asset-cache", "training-lora", "generated",
}
MAX_SCAN_DIRECTORIES = 2500
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_IMAGE_PIXELS = 100_000_000
MAX_METADATA_CHARS = 250_000
MAX_FLAT_ITEMS = 1500
MAX_IDENTIFIER_CHARS = 180
INVENTORY_FIELDS = [
    "relative_path", "extension", "size_bytes", "width", "height",
    "resolution", "mode", "has_alpha", "sha256", "metadata_present",
    "metadata_key_names", "prompt_present", "prompt_char_count",
    "negative_prompt_present", "base_model_identifier", "base_model_hash",
    "base_model_family_hint", "lora_identifiers", "sampler", "steps",
    "cfg_scale", "seed", "read_status",
]
PROMPT_ALIASES = {"prompt", "positive_prompt", "prompt_text", "positive", "caption", "text"}
NEGATIVE_ALIASES = {"negative_prompt", "negative_prompt_text", "negative", "uc"}
MODEL_ALIASES = {
    "model", "model_name", "model_id", "base_model", "base_model_name",
    "base_model_identifier", "checkpoint", "checkpoint_name", "ckpt_name",
    "ckpt", "model_identifier", "model_path",
}
HASH_ALIASES = {"model_hash", "base_model_hash", "checkpoint_hash", "ckpt_hash"}
PARAM_RE = re.compile(
    r"\b(Steps|Sampler|CFG scale|CFG|Seed|Model hash|Model)\s*:\s*([^,\n]+)",
    re.IGNORECASE,
)
LORA_TAG_RE = re.compile(r"<lora:([^:>]+):([^>]+)>", re.IGNORECASE)


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def _safe_text(value: Any, limit: int = MAX_METADATA_CHARS) -> str:
    if isinstance(value, bytes):
        if len(value) > 8192:
            return ""
        return value.decode("utf-8", errors="replace").strip()
    if isinstance(value, (str, int, float, bool)):
        return str(value).strip()[:limit]
    if value is None:
        return ""
    return ""


def _flatten_metadata(data: Any, prefix: str = "", depth: int = 0,
                      output: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]:
    output = output if output is not None else []
    if depth > 6 or len(output) >= MAX_FLAT_ITEMS:
        return output
    if isinstance(data, dict):
        for key, value in list(data.items())[:MAX_FLAT_ITEMS]:
            _flatten_metadata(value, f"{prefix}.{key}" if prefix else str(key), depth + 1, output)
            if len(output) >= MAX_FLAT_ITEMS:
                break
        return output
    if isinstance(data, (list, tuple)):
        for index, value in enumerate(data[:MAX_FLAT_ITEMS]):
            _flatten_metadata(value, f"{prefix}[{index}]", depth + 1, output)
            if len(output) >= MAX_FLAT_ITEMS:
                break
        return output
    text = _safe_text(data)
    if not text:
        return output
    if text[:1] in "{[" and len(text) <= MAX_METADATA_CHARS and depth < 6:
        try:
            nested = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            nested = None
        if isinstance(nested, (dict, list)):
            return _flatten_metadata(nested, prefix, depth + 1, output)
    output.append((prefix, text))
    return output


def _pick(flat: list[tuple[str, str]], aliases: set[str]) -> str:
    for key, value in flat:
        leaf = key.rsplit(".", 1)[-1].split("[", 1)[0]
        if _norm(leaf) in aliases and value.strip():
            return value.strip()
    return ""


def _safe_identifier(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    # Do not disclose local account names or full absolute paths from image metadata.
    if re.match(r"^[a-zA-Z]:[\\/]", value) or value.startswith(("/", "\\\\")):
        value = Path(value.replace("\\", "/")).name or "[local path redacted]"
    value = " ".join(value.replace("\x00", "").split())
    return value[:MAX_IDENTIFIER_CHARS]


def _parse_parameters(text: str) -> dict[str, str]:
    """Extract only non-prompt settings from common PNG parameter blocks."""
    found: dict[str, str] = {}
    if not text or len(text) > MAX_METADATA_CHARS:
        return found
    for match in PARAM_RE.finditer(text):
        key, value = match.group(1).lower(), match.group(2).strip()
        if key == "model":
            found.setdefault("base_model_identifier", _safe_identifier(value))
        elif key == "model hash":
            found.setdefault("base_model_hash", _safe_identifier(value))
        elif key == "sampler":
            found.setdefault("sampler", _safe_identifier(value))
        elif key in {"cfg", "cfg scale"}:
            found.setdefault("cfg_scale", _safe_identifier(value))
        elif key == "steps":
            found.setdefault("steps", _safe_identifier(value))
        elif key == "seed":
            found.setdefault("seed", _safe_identifier(value))
    return found


def _family_hint(model: str) -> str:
    lower = (model or "").lower()
    if not lower:
        return "unknown"
    if any(token in lower for token in ("sdxl", "stable-diffusion-xl", "stable_diffusion_xl")):
        return "sdxl-hint"
    if any(token in lower for token in ("stable-diffusion-v1-5", "stable-diffusion-v1.5",
                                        "sd15", "sd-1.5", "sd_1_5", "v1-5")):
        return "sd-1.5-hint"
    if "stable-diffusion" in lower or "stable_diffusion" in lower:
        return "stable-diffusion-family-hint"
    return "unknown"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_record(path: Path, root: Path, include_hash: bool = True) -> dict[str, str]:
    relative = path.relative_to(root).as_posix()
    size = path.stat().st_size
    row = {field: "" for field in INVENTORY_FIELDS}
    row.update({
        "relative_path": relative,
        "extension": path.suffix.lower(),
        "size_bytes": str(size),
        "has_alpha": "unknown",
        "metadata_present": "false",
        "prompt_present": "false",
        "negative_prompt_present": "false",
        "base_model_family_hint": "unknown",
        "read_status": "ok",
    })
    if include_hash and size <= MAX_FILE_BYTES:
        try:
            row["sha256"] = sha256_file(path)
        except OSError:
            row["read_status"] = "hash_error"
    elif size > MAX_FILE_BYTES:
        row["read_status"] = "file_over_100mb_hash_skipped"

    try:
        # Open only headers/metadata; deliberately never call image.load().
        with Image.open(path) as image:
            row["width"] = str(image.width)
            row["height"] = str(image.height)
            row["resolution"] = f"{image.width}x{image.height}"
            row["mode"] = image.mode
            row["has_alpha"] = str("A" in image.getbands() or "transparency" in image.info).lower()
            pixels = image.width * image.height
            if pixels > MAX_IMAGE_PIXELS:
                row["read_status"] = "pixel_limit_metadata_only"
                return row
            info = dict(image.info)
            try:
                for tag, value in image.getexif().items():
                    info.setdefault(f"EXIF:{ExifTags.TAGS.get(tag, str(tag))}", value)
            except Exception:
                pass
    except Exception as exc:
        row["read_status"] = f"image_read_error:{type(exc).__name__}"
        return row

    flat = _flatten_metadata(info)
    keys = sorted({key for key, _ in flat if key})
    row["metadata_key_names"] = "; ".join(keys)[:700]
    gen_words = ("prompt", "model", "lora", "adapter", "parameter", "workflow", "seed", "sampler", "steps", "cfg")
    row["metadata_present"] = str(any(any(word in _norm(k) for word in gen_words) for k in keys)).lower()

    positive = _pick(flat, PROMPT_ALIASES)
    negative = _pick(flat, NEGATIVE_ALIASES)
    row["prompt_present"] = str(bool(positive)).lower()
    row["prompt_char_count"] = str(len(positive)) if positive else "0"
    row["negative_prompt_present"] = str(bool(negative)).lower()

    selected = {
        "base_model_identifier": _safe_identifier(_pick(flat, MODEL_ALIASES)),
        "base_model_hash": _safe_identifier(_pick(flat, HASH_ALIASES)),
        "sampler": _safe_identifier(_pick(flat, {"sampler", "sampler_name", "sampling_method"})),
        "steps": _safe_identifier(_pick(flat, {"steps", "num_steps", "sampling_steps"})),
        "cfg_scale": _safe_identifier(_pick(flat, {"cfg", "cfg_scale", "guidance_scale", "guidance"})),
        "seed": _safe_identifier(_pick(flat, {"seed", "random_seed"})),
    }
    for _, value in flat:
        if "parameters" in value.lower() or "negative prompt:" in value.lower() or "sampler:" in value.lower():
            parsed = _parse_parameters(value)
            for key, parsed_value in parsed.items():
                selected.setdefault(key, parsed_value)
                if not selected.get(key):
                    selected[key] = parsed_value
    for key, value in selected.items():
        if value:
            row[key] = value
    row["base_model_family_hint"] = _family_hint(row["base_model_identifier"])

    loras: list[str] = []
    for key, value in flat:
        if len(value) <= 500:
            for match in LORA_TAG_RE.finditer(value):
                item = f"{match.group(1).strip()}@{match.group(2).strip()}"
                if item not in loras:
                    loras.append(item)
        norm_key = _norm(key).rsplit("_", 1)[-1]
        if ("lora" in _norm(key) or "adapter" in _norm(key)) and value and len(value) <= 120:
            if len(value.splitlines()) == 1 and value not in loras:
                loras.append(value)
    row["lora_identifiers"] = "; ".join(loras[:12])[:600]
    # Prompts and negative prompt text are intentionally never copied to any report.
    return row


def _skip_directory(name: str) -> bool:
    return name.startswith(".") or name.lower() in SKIP_DIRS


def scan_images(root: Path, max_files: int = 1500) -> tuple[list[dict[str, str]], dict[str, Any]]:
    records: list[dict[str, str]] = []
    counters: Counter[str] = Counter()
    visited = 0
    limit_hit = False
    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories
            if not _skip_directory(name) and not (current_path / name).is_symlink()
        )
        visited += 1
        if visited > MAX_SCAN_DIRECTORIES:
            counters["directories_skipped_after_limit"] += len(directories)
            limit_hit = True
            break
        for filename in sorted(filenames):
            path = current_path / filename
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            if path.is_symlink() or not path.is_file():
                counters["symlinks_or_nonregular_skipped"] += 1
                continue
            if len(records) >= max_files:
                limit_hit = True
                counters["images_skipped_after_file_limit"] += 1
                continue
            try:
                records.append(_image_record(path, root))
            except OSError:
                counters["stat_errors"] += 1
            counters["images_scanned"] += 1
            if len(records) % 25 == 0:
                print(f"Analizadas {len(records)} imágenes...", flush=True)
        if visited >= MAX_SCAN_DIRECTORIES:
            limit_hit = bool(directories)
            if limit_hit:
                counters["directories_skipped_after_limit"] += len(directories)
                break
    counters["directories_visited"] = visited
    return records, {
        "scan_limits": {
            "maximum_directories": MAX_SCAN_DIRECTORIES,
            "maximum_images": max_files,
            "maximum_hash_file_size_bytes": MAX_FILE_BYTES,
            "maximum_metadata_pixel_count": MAX_IMAGE_PIXELS,
        },
        "truncated_by_safety_limit": limit_hit,
        "counts": dict(sorted(counters.items())),
    }


def get_memory_info() -> dict[str, Any]:
    if os.name == "nt":
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MEMORYSTATUSEX()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return {
                    "total_ram_bytes": int(status.ullTotalPhys),
                    "available_ram_bytes": int(status.ullAvailPhys),
                    "memory_load_percent": int(status.dwMemoryLoad),
                }
        except Exception:
            pass
    try:
        pagesize = os.sysconf("SC_PAGE_SIZE")
        total = os.sysconf("SC_PHYS_PAGES") * pagesize
        available = os.sysconf("SC_AVPHYS_PAGES") * pagesize
        return {"total_ram_bytes": int(total), "available_ram_bytes": int(available),
                "memory_load_percent": round((total - available) / total * 100) if total else None}
    except (ValueError, OSError, AttributeError):
        return {"total_ram_bytes": None, "available_ram_bytes": None, "memory_load_percent": None}


def _windows_hardware_names() -> dict[str, Any]:
    info: dict[str, Any] = {"cpu_name": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", ""),
                            "gpu_adapters": []}
    if os.name != "nt":
        return info
    try:
        import winreg
        cpu_key = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, cpu_key) as key:
            try:
                info["cpu_name"] = str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
            except OSError:
                pass
        video_key = r"SYSTEM\CurrentControlSet\Control\Video"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, video_key) as video_root:
                count = winreg.QueryInfoKey(video_root)[0]
                found: set[tuple[str, str]] = set()
                for index in range(min(count, 32)):
                    try:
                        subkey = winreg.EnumKey(video_root, index) + r"\0000"
                        with winreg.OpenKey(video_root, subkey) as adapter:
                            try:
                                name = str(winreg.QueryValueEx(adapter, "DriverDesc")[0]).strip()
                            except OSError:
                                continue
                            try:
                                driver = str(winreg.QueryValueEx(adapter, "DriverVersion")[0]).strip()
                            except OSError:
                                driver = ""
                            pair = (name, driver)
                            if pair in found:
                                continue
                            found.add(pair)
                            info["gpu_adapters"].append({"name": name, "driver_version": driver or None})
                info["gpu_adapter_names_source"] = "Windows video-adapter registry; best effort"
        except OSError:
            info["gpu_adapter_names_source"] = "not available from registry"
    except Exception:
        info["hardware_probe_note"] = "Windows registry probe unavailable"
    return info


def audit_manifest(root: Path) -> dict[str, Any] | None:
    path = root / "data" / "training-labels.csv"
    if not path.is_file():
        return None
    row_count = 0
    approvals = {
        key: Counter()
        for key in ("visual_review", "license_review", "training_permission")
    }
    source_models = Counter()
    seen_paths: set[str] = set()
    duplicate_paths = 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                return {"found": True, "parse_error": "missing_header"}
            for row in reader:
                row_count += 1
                rel = (row.get("path") or "").strip()
                if rel:
                    if rel in seen_paths:
                        duplicate_paths += 1
                    seen_paths.add(rel)
                for key, counter in approvals.items():
                    counter[(row.get(key) or "").strip().lower() or "blank"] += 1
                model = _safe_identifier(row.get("base_model_identifier") or "")
                if model:
                    source_models[model] += 1
    except (OSError, UnicodeError, csv.Error):
        return {"found": True, "parse_error": "csv_read_error"}
    return {
        "found": True,
        "row_count": row_count,
        "unique_paths": len(seen_paths),
        "duplicate_paths": duplicate_paths,
        "review_state_counts": {key: dict(sorted(counter.items())) for key, counter in approvals.items()},
        "top_source_model_identifiers": [
            {"identifier": name, "row_count": count}
            for name, count in source_models.most_common(15)
        ],
        "source_note": "No image rows or prompt text from this manifest are copied into the summary."
    }


def scan_local_models(models_root: Path | None) -> dict[str, Any]:
    if models_root is None or not models_root.is_dir():
        return {"models_root_found": False, "model_candidates": [], "lora_file_names": []}
    model_candidates: list[dict[str, Any]] = []
    model_dirs: set[Path] = set()
    visited = 0
    for current, dirs, files in os.walk(models_root, topdown=True, followlinks=False):
        here = Path(current)
        dirs[:] = sorted(d for d in dirs if not _skip_directory(d) and not (here / d).is_symlink())
        visited += 1
        if visited > 400:
            break
        if "model_index.json" not in files:
            continue
        model_dirs.add(here.resolve())
        try:
            index = json.loads((here / "model_index.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            model_candidates.append({"relative_path": here.relative_to(models_root).as_posix(),
                                     "status": "unreadable_model_index"})
            continue
        class_name = str(index.get("_class_name", ""))
        if class_name == "StableDiffusionPipeline":
            family = "sd"
            components = ("unet", "vae", "scheduler", "tokenizer", "text_encoder")
        elif class_name == "StableDiffusionXLPipeline":
            family = "sdxl"
            components = ("unet", "vae", "scheduler", "tokenizer", "text_encoder", "tokenizer_2", "text_encoder_2")
        else:
            family = "unsupported_or_unknown"
            components = ()
        present = [name for name in components if (here / name).is_dir() and not (here / name).is_symlink()]
        missing = sorted(set(components) - set(present))
        model_candidates.append({
            "relative_path": here.relative_to(models_root).as_posix(),
            "pipeline_class": class_name or "unknown",
            "family_hint": family,
            "component_directories_present": present,
            "missing_component_directories": missing,
            "status": "directory_structure_only_not_load_tested" if not missing and components else "incomplete_or_unsupported",
        })
    loras: list[str] = []
    for current, dirs, files in os.walk(models_root, topdown=True, followlinks=False):
        here = Path(current)
        dirs[:] = sorted(d for d in dirs if not _skip_directory(d) and not (here / d).is_symlink())
        for name in sorted(files):
            candidate = here / name
            if candidate.suffix.lower() != ".safetensors" or candidate.is_symlink():
                continue
            resolved_parent = here.resolve()
            if any(resolved_parent == model_dir or model_dir in resolved_parent.parents for model_dir in model_dirs):
                continue
            loras.append(candidate.relative_to(models_root).as_posix())
            if len(loras) >= 100:
                break
        if len(loras) >= 100:
            break
    return {
        "models_root_found": True,
        "models_root_label": models_root.name,
        "directories_visited": visited,
        "model_candidates": model_candidates[:100],
        "lora_file_names": loras,
        "weights_were_not_opened": True,
        "model_loading_was_not_attempted": True,
    }


def build_summary(root: Path, records: list[dict[str, str]], scan: dict[str, Any],
                  include_hashes: bool, started_at: str, duration_seconds: float,
                  memory_before: dict[str, Any], memory_after: dict[str, Any],
                  hardware: dict[str, Any], manifest: dict[str, Any] | None,
                  models: dict[str, Any]) -> dict[str, Any]:
    base_models = Counter(row["base_model_identifier"] for row in records if row["base_model_identifier"])
    model_hashes = Counter(row["base_model_hash"] for row in records if row["base_model_hash"])
    loras = Counter()
    for row in records:
        for value in row["lora_identifiers"].split(";"):
            value = value.strip()
            if value:
                loras[value] += 1
    resolutions = Counter(row["resolution"] for row in records if row["resolution"])
    statuses = Counter(row["read_status"] for row in records)
    duplicate_hash_groups: dict[str, list[str]] = {}
    if include_hashes:
        for row in records:
            sha = row["sha256"]
            if sha:
                duplicate_hash_groups.setdefault(sha, []).append(row["relative_path"])
    duplicate_groups = [
        {"sha256": sha, "count": len(paths), "sample_relative_paths": paths[:5]}
        for sha, paths in duplicate_hash_groups.items() if len(paths) > 1
    ]
    return {
        "tool": {"name": "IMAGE Local Diagnostic", "version": APP_VERSION},
        "created_at_local": started_at,
        "selected_folder_label": root.name or "selected-root",
        "privacy": {
            "prompt_text_in_reports": False,
            "negative_prompt_text_in_reports": False,
            "absolute_collection_path_in_reports": False,
            "network_requests_made": False,
            "source_images_modified": False,
            "model_weights_opened": False,
            "model_inference_or_training_run": False,
        },
        "hardware": {
            **hardware,
            "logical_cpu_count": os.cpu_count(),
            "architecture": platform.machine(),
            "python_runtime": platform.python_version(),
            "platform": platform.platform(),
            "ram_before_scan": memory_before,
            "ram_after_scan": memory_after,
        },
        "scan": {
            **scan,
            "image_count": len(records),
            "images_with_generation_metadata_hint": sum(r["metadata_present"] == "true" for r in records),
            "images_with_prompt_metadata_present": sum(r["prompt_present"] == "true" for r in records),
            "images_with_negative_prompt_metadata_present": sum(r["negative_prompt_present"] == "true" for r in records),
            "images_with_base_model_identifier": sum(bool(r["base_model_identifier"]) for r in records),
            "images_with_base_model_hash": sum(bool(r["base_model_hash"]) for r in records),
            "images_with_lora_identifiers": sum(bool(r["lora_identifiers"]) for r in records),
            "read_status_counts": dict(sorted(statuses.items())),
            "top_resolutions": [{"resolution": k, "count": v} for k, v in resolutions.most_common(12)],
            "observed_base_model_identifiers": [{"identifier": k, "image_count": v} for k, v in base_models.most_common(20)],
            "observed_base_model_hashes": [{"hash": k, "image_count": v} for k, v in model_hashes.most_common(20)],
            "observed_lora_identifiers": [{"identifier": k, "image_count": v} for k, v in loras.most_common(30)],
            "exact_duplicate_group_count": len(duplicate_groups),
            "exact_duplicate_copies_beyond_first": sum(x["count"] - 1 for x in duplicate_groups),
            "exact_duplicate_groups_sample": duplicate_groups[:30],
            "elapsed_seconds": round(duration_seconds, 2),
            "hashes_computed": include_hashes,
        },
        "training_manifest": manifest,
        "local_models": models,
        "notes": [
            "Metadata identifiers are hints, not proof of ownership, license, training permission, or model compatibility.",
            "Model candidates were inspected structurally only; weights were not loaded and no generation was attempted.",
            "Images were opened for headers/metadata only; pixel data was not decoded into full-resolution arrays.",
            "Exact duplicate groups are based on SHA-256 only; visually similar images may have different hashes.",
            "Prompt and negative-prompt text are deliberately excluded. Only their presence and prompt character count are reported.",
            "Rows marked approved in a manifest reflect the local file's current labels; this tool does not approve/review licensing.",
        ],
    }


def _write_readme(path: Path) -> None:
    path.write_text(
        "IMAGE Local Diagnostic - result bundle\n\n"
        "Contains diagnostic_summary.json and image_inventory.csv.\n"
        "This tool is read-only for the source images and makes no network requests.\n"
        "Prompt and negative-prompt text are excluded; only presence and prompt length are reported.\n"
        "The report contains relative filenames, image SHA-256 hashes, metadata key names, model/LoRA identifiers,\n"
        "coarse hardware information, and current manifest review-state counts.\n\n"
        "Before sharing this ZIP, review the relative filenames and model identifiers in the CSV/JSON.\n"
        "The ZIP is not uploaded automatically. Attach it to the IMAGE support conversation only when you choose.\n"
        "No model weights or source images are included.\n",
        encoding="utf-8",
    )


def run_diagnostic(root: Path, output: Path, max_files: int = 1500,
                   include_hashes: bool = True) -> Path:
    root = root.expanduser().resolve()
    output = output.expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Selected image folder does not exist or is not a directory.")
    if output == root or root in output.parents:
        raise ValueError("Reports must be saved outside the selected source folder.")
    start_clock = time.monotonic()
    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    memory_before = get_memory_info()
    hardware = _windows_hardware_names()
    print("IMAGE Diagnostic: read-only mode; no network, no training, no model loading.", flush=True)
    print(f"Carpeta seleccionada: {root.name or 'raíz'}", flush=True)
    records, scan = scan_images(root, max_files)
    memory_after = get_memory_info()
    models_root = root / "models"
    models = scan_local_models(models_root if models_root.is_dir() else None)
    manifest = audit_manifest(root)
    duration = time.monotonic() - start_clock

    output.mkdir(parents=True, exist_ok=False)
    csv_path = output / "image_inventory.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INVENTORY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    summary = build_summary(root, records, scan, include_hashes, started_at, duration,
                            memory_before, memory_after, hardware, manifest, models)
    json_path = output / "diagnostic_summary.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme_path = output / "READ_BEFORE_SHARING.txt"
    _write_readme(readme_path)
    zip_path = output / "IMAGE-Diagnostic-Bundle.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        bundle.write(json_path, arcname=json_path.name)
        bundle.write(csv_path, arcname=csv_path.name)
        bundle.write(readme_path, arcname=readme_path.name)
    checksum = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (output / "IMAGE-Diagnostic-Bundle.zip.sha256").write_text(
        f"{checksum}  {zip_path.name}\n", encoding="ascii"
    )
    print(f"Imágenes analizadas: {len(records)}", flush=True)
    print(f"Metadatos tipo generación: {summary['scan']['images_with_generation_metadata_hint']}", flush=True)
    print(f"Modelo base identificado: {summary['scan']['images_with_base_model_identifier']}", flush=True)
    print(f"LoRA identificada: {summary['scan']['images_with_lora_identifiers']}", flush=True)
    print(f"Informe ZIP: {zip_path}", flush=True)
    print("No se copiaron imágenes ni textos de prompt y no se envió información por red.", flush=True)
    return zip_path


def select_folder(title: str, initial: Path | None = None) -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog

        window = tk.Tk()
        window.withdraw()
        try:
            window.attributes("-topmost", True)
        except Exception:
            pass
        selected = filedialog.askdirectory(
            parent=window, title=title,
            initialdir=str(initial) if initial and initial.is_dir() else str(Path.home()),
            mustexist=True,
        )
        window.destroy()
        return Path(selected).expanduser().resolve() if selected else None
    except Exception:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Specific folder containing IMAGE/reference images")
    parser.add_argument("--output", type=Path, help="Output folder; must be outside --root")
    parser.add_argument("--max-files", type=int, default=1500, help="Safety cap for images scanned (default: 1500)")
    parser.add_argument("--no-hash", action="store_true", help="Skip image SHA-256 for a faster but less complete report")
    parser.add_argument("--self-test", action="store_true", help="Run a small offline self-test and exit")
    parser.add_argument("--version", action="version", version=f"IMAGE Local Diagnostic {APP_VERSION}")
    return parser


def self_test() -> int:
    from PIL.PngImagePlugin import PngInfo

    with tempfile.TemporaryDirectory(prefix="image-diagnostic-test-") as directory:
        temp = Path(directory)
        root = temp / "source"
        root.mkdir()
        meta = PngInfo()
        meta.add_text(
            "parameters",
            "PRIVATE_PROMPT_SENTINEL\\nNegative prompt: PRIVATE_NEGATIVE_SENTINEL\\n"
            "Steps: 12, Sampler: Euler a, CFG scale: 7, Seed: 42, Model hash: abc123"
        )
        image_path = root / "sample.png"
        Image.new("RGB", (32, 48), (20, 30, 40)).save(image_path, pnginfo=meta)
        output = temp / "reports"
        zip_path = run_diagnostic(root, output, max_files=10)
        with zipfile.ZipFile(zip_path) as bundle:
            all_text = "".join(
                bundle.read(name).decode("utf-8", errors="replace")
                for name in bundle.namelist() if name.endswith((".json", ".csv", ".txt"))
            )
            assert "PRIVATE_PROMPT_SENTINEL" not in all_text
            assert "PRIVATE_NEGATIVE_SENTINEL" not in all_text
            assert "sample.png" in all_text
            assert "32x48" in all_text
        print("SELF-TEST PASSED: files created, metadata summarized, no prompt text leaked.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.max_files <= 5000:
        parser.error("--max-files must be between 1 and 5000.")
    if args.self_test:
        return self_test()
    root = args.root.expanduser().resolve() if args.root else select_folder(
        "IMAGE: select the project or folder containing the original/reference images"
    )
    if root is None:
        print("No folder selected; no files were scanned.", file=sys.stderr)
        return 2
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    default_output = root.parent / f"{root.name or 'IMAGE'}-DIAGNOSTIC-{stamp}"
    if default_output == root or root in default_output.parents:
        default_output = Path(tempfile.gettempdir()) / f"IMAGE-DIAGNOSTIC-{stamp}"
    output = args.output.expanduser().resolve() if args.output else default_output
    if output == root or root in output.parents:
        parser.error("--output must point outside the selected image/source folder.")
    try:
        run_diagnostic(root, output, max_files=args.max_files, include_hashes=not args.no_hash)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Diagnostic failed safely: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if not args.root:
        try:
            input("Listo. Revisa el ZIP indicado arriba. Pulsa Enter para cerrar.")
        except (EOFError, KeyboardInterrupt):
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
