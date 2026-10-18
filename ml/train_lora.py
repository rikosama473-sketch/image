#!/usr/bin/env python3
"""Train an IMAGE style LoRA using a pinned Hugging Face Diffusers trainer.

This launcher does not download model weights by default, never edits source
images, and refuses to train until image review, licensing, permissions,
captions, and the source-family confirmation pass preflight checks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRAINER_VERSION = "v0.35.1"
TRAINER_CACHE = ROOT / "data" / "cache" / f"diffusers-{TRAINER_VERSION}"
STAGING_ROOT = ROOT / "data" / "cache" / "lora-training"
TRAINER_SOURCES = {
    "sd": {
        "filename": "train_text_to_image_lora.py",
        "relative_path": "examples/text_to_image/train_text_to_image_lora.py",
        "blob_sha": "0eff8f9c9b8cbaf428d8d164f5b075ff30a63299",
    },
    "sdxl": {
        "filename": "train_text_to_image_lora_sdxl.py",
        "relative_path": "examples/text_to_image/train_text_to_image_lora_sdxl.py",
        "blob_sha": "88148c1924ca7b95702cb7bb9fce3be445c33292",
    },
}
APPROVED = "approved"
LABEL_FIELDS = ("visual_review", "license_review", "training_permission")


def normalise_repo_path(value: str) -> str:
    return Path(value.strip().replace("\\", "/")).as_posix()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader)


def source_manifest_paths(labels_path: Path, root: Path) -> list[dict[str, str]]:
    rows = read_csv(labels_path)
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        relative = normalise_repo_path(row.get("path", ""))
        if not relative or relative == ".":
            continue
        if relative in seen:
            raise ValueError(f"Duplicate image path in labels CSV: {relative}")
        seen.add(relative)
        row["path"] = relative
        result.append(row)
    if not result:
        raise ValueError(f"No image paths found in labels CSV: {labels_path}")
    return result


def make_caption_template(
    labels_path: Path, output: Path, root: Path = ROOT, overwrite: bool = False
) -> int:
    rows = source_manifest_paths(labels_path, root)
    output = output.expanduser()
    if not output.is_absolute():
        output = root / output
    output = output.resolve()
    if output == labels_path.resolve():
        raise ValueError("Caption template cannot overwrite the original training-labels CSV.")
    for row in rows:
        source = (root / row["path"]).resolve()
        if output == source:
            raise ValueError(f"Caption template cannot overwrite a source image: {source}")
    if output.exists() and not overwrite:
        raise FileExistsError(
            f"Caption template already exists: {output}. Move it aside or pass --overwrite-caption-template explicitly."
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "caption"], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({"path": row["path"], "caption": ""})
    return len(rows)


def fetch_official_trainers() -> list[Path]:
    """Download and verify upstream scripts only when explicitly requested."""
    TRAINER_CACHE.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for family, source in TRAINER_SOURCES.items():
        destination = TRAINER_CACHE / source["filename"]
        if destination.is_file():
            data = destination.read_bytes()
            if git_blob_sha(data) != source["blob_sha"]:
                raise ValueError(
                    f"Cached trainer failed integrity verification: {destination}. "
                    "Move it aside and rerun --fetch-official-trainers."
                )
            saved.append(destination)
            continue
        url = f"https://raw.githubusercontent.com/huggingface/diffusers/{TRAINER_VERSION}/{source['relative_path']}"
        request = urllib.request.Request(url, headers={"User-Agent": "IMAGE-local-lora-trainer/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(200_001)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Could not download official Diffusers trainer for {family}: {exc}") from exc
        if len(data) > 200_000:
            raise ValueError(f"Unexpectedly large trainer response from {url}; refusing to save it.")
        if git_blob_sha(data) != source["blob_sha"]:
            raise ValueError(f"Integrity check failed for official trainer {url}; file was not saved.")
        destination.write_bytes(data)
        saved.append(destination)
    return saved


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def detect_model_family(model: str, requested_family: str, allow_download: bool) -> tuple[str, str, bool]:
    candidate = Path(model).expanduser()
    if candidate.exists():
        if not candidate.is_dir():
            raise ValueError(
                "Training expects a Diffusers model directory with model_index.json, not a single checkpoint file."
            )
        index_path = candidate / "model_index.json"
        if not index_path.is_file():
            raise ValueError(f"Missing model_index.json in local model directory: {candidate}")
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read {index_path}: {exc}") from exc
        class_name = str(index.get("_class_name", ""))
        classes = {
            "StableDiffusionPipeline": "sd",
            "StableDiffusionXLPipeline": "sdxl",
        }
        detected = classes.get(class_name)
        if detected is None:
            raise ValueError(
                f"Unsupported model pipeline class {class_name!r}. This trainer currently supports "
                "StableDiffusionPipeline and StableDiffusionXLPipeline only; no model family was guessed."
            )
        if requested_family != "auto" and requested_family != detected:
            raise ValueError(
                f"--family={requested_family} conflicts with model_index.json class {class_name} ({detected})."
            )
        return detected, str(candidate.resolve()), True

    if requested_family == "auto":
        raise ValueError(
            "The model is not a local directory, so its family cannot be inspected. "
            "Provide --family sd or --family sdxl explicitly."
        )
    if not allow_download:
        # A hub identifier may still work from the local cache because the run is offline by default.
        return requested_family, model, False
    return requested_family, model, False


def load_captions(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    rows = read_csv(path)
    fieldnames = set(rows[0].keys()) if rows else set()
    if not {"path", "caption"}.issubset(fieldnames):
        raise ValueError(f"Captions CSV must contain path and caption columns: {path}")
    captions: dict[str, str] = {}
    for row in rows:
        relative = normalise_repo_path(row.get("path", ""))
        if not relative:
            continue
        if relative in captions:
            raise ValueError(f"Duplicate path in captions CSV: {relative}")
        captions[relative] = (row.get("caption") or "").strip()
    return captions


def load_metadata(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    rows = read_csv(path)
    if rows and not {"path", "base_model_identifier"}.issubset(set(rows[0].keys())):
        raise ValueError(f"Metadata CSV must contain path and base_model_identifier columns: {path}")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        relative = normalise_repo_path(row.get("path", ""))
        if relative:
            if relative in result:
                raise ValueError(f"Duplicate path in metadata CSV: {relative}")
            result[relative] = row
    return result


def load_approved_examples(
    labels_path: Path,
    root: Path,
    captions_path: Path | None,
    metadata_path: Path | None,
) -> tuple[list[dict[str, str]], Counter[str], list[str]]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required. Install the lightweight requirements.txt first.") from exc

    rows = source_manifest_paths(labels_path, root)
    captions = load_captions(captions_path)
    metadata = load_metadata(metadata_path)
    skipped = Counter()
    examples: list[dict[str, str]] = []
    caption_missing: list[str] = []
    for row in rows:
        statuses = [str(row.get(field, "")).strip().lower() for field in LABEL_FIELDS]
        if any(status != APPROVED for status in statuses):
            skipped["not_fully_approved"] += 1
            continue
        relative = row["path"]
        source = (root / relative).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            skipped["missing_or_unsafe_file"] += 1
            continue
        try:
            with Image.open(source) as image:
                image.verify()
        except (OSError, ValueError):
            skipped["unreadable_image"] += 1
            continue
        caption = captions.get(relative, "").strip() or str(row.get("caption", "")).strip()
        if not caption:
            caption_missing.append(relative)
            continue
        if len(caption) > 1500:
            raise ValueError(f"Caption exceeds 1500 characters for {relative}.")
        metadata_row = metadata.get(relative, {})
        source_model = (
            str(metadata_row.get("base_model_identifier", "")).strip()
            or str(row.get("base_model_identifier", "")).strip()
        )
        examples.append({
            "path": relative,
            "absolute_path": str(source),
            "caption": caption,
            "source_model": source_model,
        })
    if caption_missing:
        sample = ", ".join(caption_missing[:5])
        raise ValueError(
            f"{len(caption_missing)} fully approved images have no caption. "
            f"Fill the caption column in --captions-csv (for example the generated template). "
            f"First missing paths: {sample}"
        )
    return examples, skipped, [str(key) for key in metadata]


def verify_source_models(
    examples: list[dict[str, str]],
    allow_unknown: bool,
    allow_multiple: bool,
) -> tuple[Counter[str], int]:
    observed = Counter(example["source_model"] for example in examples if example["source_model"])
    unknown_count = sum(1 for example in examples if not example["source_model"])
    if unknown_count and not allow_unknown:
        raise ValueError(
            f"{unknown_count} approved images have no confirmed source base-model identifier. "
            "Review the metadata report/labels, or explicitly use --allow-unknown-source-models "
            "after reviewing the dataset family."
        )
    if len(observed) > 1 and not allow_multiple:
        names = ", ".join(f"{name} ({count})" for name, count in observed.most_common(8))
        raise ValueError(
            f"Approved images reference {len(observed)} distinct source checkpoint identifiers: {names}. "
            "Review their compatibility and split incompatible groups, or explicitly use "
            "--allow-multiple-source-models after verifying they share a compatible family."
        )
    return observed, unknown_count


def stage_image(source: Path, target: Path) -> None:
    try:
        target.symlink_to(source)
        return
    except OSError:
        pass
    try:
        os.link(source, target)
        return
    except OSError:
        pass
    shutil.copy2(source, target)


def prepare_imagefolder(
    examples: list[dict[str, str]],
    staging_dir: Path,
    seed: int,
    validation_ratio: float,
) -> tuple[Path, Path, list[dict[str, str]], list[dict[str, str]]]:
    if not 0.05 <= validation_ratio <= 0.5:
        raise ValueError("--validation-ratio must be between 0.05 and 0.5.")
    shuffled = sorted(examples, key=lambda row: row["path"].casefold())
    random.Random(seed).shuffle(shuffled)
    validation_count = max(1, int(round(len(shuffled) * validation_ratio)))
    train_rows = shuffled[:-validation_count]
    validation_rows = shuffled[-validation_count:]
    if len(train_rows) < 8:
        raise ValueError(
            f"Need at least 8 training images plus a held-out validation image; got "
            f"{len(train_rows)} train and {len(validation_rows)} validation. "
            "Review and approve more images before starting a LoRA run."
        )

    if staging_dir.exists():
        raise ValueError(f"Staging directory already exists; refusing to overwrite it: {staging_dir}")
    train_dir = staging_dir / "train"
    validation_dir = staging_dir / "validation"
    for split_dir, split_rows, prefix in (
        (train_dir, train_rows, "train"),
        (validation_dir, validation_rows, "validation"),
    ):
        images_dir = split_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=False)
        metadata_lines: list[str] = []
        for index, row in enumerate(split_rows, start=1):
            suffix = Path(row["path"]).suffix.lower()
            if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
                suffix = ".png"
            image_name = f"{prefix}-{index:05d}{suffix}"
            target = images_dir / image_name
            stage_image(Path(row["absolute_path"]), target)
            metadata_lines.append(json.dumps(
                {"file_name": f"images/{image_name}", "text": row["caption"]},
                ensure_ascii=False,
            ))
        (split_dir / "metadata.jsonl").write_text(
            "\n".join(metadata_lines) + "\n", encoding="utf-8"
        )
    return train_dir, validation_dir, train_rows, validation_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--make-caption-template",
        action="store_true",
        help="Write a local path/caption CSV template; this does not approve images or train a model.",
    )
    actions.add_argument(
        "--fetch-official-trainers",
        action="store_true",
        help="Download and verify the pinned official Diffusers v0.35.1 LoRA scripts; no weights are downloaded.",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root containing the approved images")
    parser.add_argument("--labels", type=Path, default=Path("data/training-labels.csv"))
    parser.add_argument("--captions-csv", type=Path, help="Reviewed local CSV with path,caption columns")
    parser.add_argument("--metadata-csv", type=Path, help="Local report from extract_generation_metadata.py")
    parser.add_argument("--caption-template-output", type=Path, default=Path("data/cache/lora-captions-template.csv"))
    parser.add_argument("--overwrite-caption-template", action="store_true", help="Explicitly overwrite an existing caption template, never the labels manifest or source images")
    parser.add_argument("--model", help="Local Diffusers directory or an explicit/cached model identifier")
    parser.add_argument("--family", choices=("auto", "sd", "sdxl"), default="auto")
    parser.add_argument(
        "--confirm-source-family",
        choices=("sd", "sdxl"),
        help="Explicitly confirm that reviewed dataset source images are compatible with the chosen model family",
    )
    parser.add_argument("--allow-model-download", action="store_true", help="Permit base-model downloads during training")
    parser.add_argument("--allow-unknown-source-models", action="store_true", help="Include approved images with unknown source checkpoint identifiers")
    parser.add_argument("--allow-multiple-source-models", action="store_true", help="Include multiple checkpoint IDs after manually verifying compatibility")
    parser.add_argument("--resolution", type=int, help="Training resolution; defaults to 512 for SD and 768 for SDXL")
    parser.add_argument("--train-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--max-train-steps", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validation-ratio", type=float, default=0.1)
    parser.add_argument("--validation-prompt", help="Optional prompt for the trainer's periodic sample images")
    parser.add_argument("--precision", choices=("auto", "no", "fp16", "bf16"), default="auto")
    parser.add_argument("--output-dir", type=Path, help="Output directory; relative paths must be under outputs/")
    parser.add_argument("--checkpointing-steps", type=int, default=250)
    parser.add_argument("--resume-from-checkpoint", help="Checkpoint folder name or 'latest' in an existing output directory")
    parser.add_argument("--check-only", action="store_true", help="Run preflight without training or staging images")
    return parser


def resolve_path(value: Path, root: Path) -> Path:
    path = value.expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def choose_output_dir(value: Path | None, seed: int, root: Path, resume: str | None) -> Path:
    if value is None:
        if resume:
            raise ValueError("--resume-from-checkpoint requires --output-dir pointing to the existing run.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        return (root / "outputs" / "training-lora" / f"run-{stamp}-seed-{seed}").resolve()
    original = value.expanduser()
    output = resolve_path(original, root)
    if output.is_relative_to(root) and not output.is_relative_to(root / "outputs"):
        raise ValueError("Output inside the repository must be under outputs/ so weights are not accidentally tracked by Git.")
    if resume:
        if resume != "latest" and (Path(resume).name != resume or not resume.startswith("checkpoint-")):
            raise ValueError("--resume-from-checkpoint must be 'latest' or a checkpoint-N folder name, without path components.")
        if not output.is_dir():
            raise ValueError("--resume-from-checkpoint requires an existing --output-dir.")
        checkpoint = output / "checkpoint-latest" if resume == "latest" else output / resume
        if resume == "latest":
            checkpoint_dirs = [p for p in output.glob("checkpoint-*") if p.is_dir()]
            if not checkpoint_dirs:
                raise ValueError(f"No checkpoint-* directory exists in {output}.")
        elif not checkpoint.is_dir():
            raise ValueError(f"Checkpoint directory not found inside output directory: {checkpoint}")
    elif output.exists() and any(output.iterdir()):
        raise ValueError(f"Output directory is not empty. Use another path or resume from a checkpoint: {output}")
    return output


def choose_precision(torch: Any, requested: str) -> str:
    cuda = bool(torch.cuda.is_available())
    if requested == "auto":
        if not cuda:
            return "no"
        try:
            return "bf16" if torch.cuda.is_bf16_supported() else "fp16"
        except (AttributeError, RuntimeError):
            return "fp16"
    if requested in {"fp16", "bf16"} and not cuda:
        raise ValueError(f"--precision {requested} requires CUDA for this training workflow; use --precision no on CPU.")
    if requested == "bf16" and not torch.cuda.is_bf16_supported():
        raise ValueError("This CUDA GPU does not report BF16 support; use --precision fp16 or auto.")
    return requested


def validate_resume_compatibility(output_dir: Path, current: dict[str, Any]) -> None:
    previous_path = output_dir / "training-config.json"
    if not previous_path.is_file():
        raise ValueError(
            "Cannot resume safely without training-config.json from the original run. "
            "Start a new output directory rather than guessing the prior dataset/configuration."
        )
    try:
        previous = json.loads(previous_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read previous training configuration: {exc}") from exc
    for key in (
        "model", "model_family", "dataset_manifest_sha256",
        "training_image_paths", "validation_image_paths",
    ):
        if previous.get(key) != current.get(key):
            raise ValueError(f"Resume refused because {key} differs from the original run.")
    previous_parameters = previous.get("parameters", {})
    current_parameters = current.get("parameters", {})
    for key in (
        "resolution", "train_batch_size", "gradient_accumulation_steps",
        "max_train_steps", "learning_rate", "rank", "seed", "precision",
        "checkpointing_steps", "validation_ratio",
    ):
        if previous_parameters.get(key) != current_parameters.get(key):
            raise ValueError(f"Resume refused because training parameter {key} differs from the original run.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.fetch_official_trainers:
        try:
            paths = fetch_official_trainers()
        except (OSError, RuntimeError, ValueError) as exc:
            parser.error(str(exc))
        for path in paths:
            print(f"Verified official trainer: {path}")
        print("Only trainer source code was downloaded; no model weights or images were uploaded.")
        return 0
    if args.make_caption_template:
        root = args.root.expanduser().resolve()
        labels = resolve_path(args.labels, root)
        output = args.caption_template_output.expanduser()
        if not output.is_absolute():
            output = root / output
        try:
            count = make_caption_template(labels, output, root, args.overwrite_caption_template)
        except (OSError, csv.Error, UnicodeError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Created local caption template for {count} manifest paths: {output.resolve()}")
        print("Captions are blank for manual review; this does not approve images or train a model.")
        return 0

    if not args.model:
        parser.error("--model is required for training. Use --make-caption-template or --fetch-official-trainers for those setup tasks.")
    if not args.confirm_source_family:
        parser.error("--confirm-source-family is required after reviewing source-model metadata and compatibility.")

    root = args.root.expanduser().resolve()
    labels_path = resolve_path(args.labels, root)
    captions_path = resolve_path(args.captions_csv, root) if args.captions_csv else None
    metadata_path = resolve_path(args.metadata_csv, root) if args.metadata_csv else None
    if not labels_path.is_file():
        parser.error(f"Labels CSV not found: {labels_path}")
    if captions_path and not captions_path.is_file():
        parser.error(f"Captions CSV not found: {captions_path}")
    if metadata_path and not metadata_path.is_file():
        parser.error(f"Metadata CSV not found: {metadata_path}")

    try:
        family, model_arg, local_model = detect_model_family(args.model, args.family, args.allow_model_download)
        if args.confirm_source_family != family:
            raise ValueError(
                f"--confirm-source-family={args.confirm_source_family} does not match the selected model family {family}."
            )
        examples, skipped, _ = load_approved_examples(labels_path, root, captions_path, metadata_path)
        if len(examples) < 9:
            raise ValueError(
                f"Only {len(examples)} fully approved and captioned images are available; "
                "at least 9 are required for 8 training images plus a held-out validation image."
            )
        source_models, unknown_sources = verify_source_models(
            examples, args.allow_unknown_source_models, args.allow_multiple_source_models
        )
        if args.train_batch_size < 1 or args.train_batch_size > 8:
            raise ValueError("--train-batch-size must be between 1 and 8.")
        if args.gradient_accumulation_steps < 1 or args.gradient_accumulation_steps > 64:
            raise ValueError("--gradient-accumulation-steps must be between 1 and 64.")
        if args.max_train_steps < 1 or args.max_train_steps > 100000:
            raise ValueError("--max-train-steps must be between 1 and 100000.")
        if not (0 < args.learning_rate <= 0.01):
            raise ValueError("--learning-rate must be greater than 0 and at most 0.01.")
        if args.rank < 1 or args.rank > 128:
            raise ValueError("--rank must be between 1 and 128.")
        if args.checkpointing_steps < 1:
            raise ValueError("--checkpointing-steps must be positive.")
        resolution = args.resolution if args.resolution is not None else (512 if family == "sd" else 768)
        if resolution < 256 or resolution > 1536 or resolution % 8:
            raise ValueError("--resolution must be between 256 and 1536 and divisible by 8.")
        if args.resume_from_checkpoint and not args.output_dir:
            raise ValueError("--resume-from-checkpoint requires --output-dir.")
        output_dir = choose_output_dir(args.output_dir, args.seed, root, args.resume_from_checkpoint)
    except (OSError, csv.Error, UnicodeError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    print(f"Model family: {family} (detected from local model_index.json or declared for the hub identifier)")
    print(f"Approved/captioned images: {len(examples)}; excluded by review/file checks: {sum(skipped.values())}")
    print(f"Observed source checkpoints: {len(source_models)}; unknown source IDs: {unknown_sources}")
    print(f"Source-checkpoint counts: {dict(source_models)}")
    print(f"Base model: {model_arg}")
    print(f"Output directory: {output_dir}")
    if unknown_sources:
        print("WARNING: unknown source model IDs were explicitly allowed; the resulting style may be less consistent.")
    if len(source_models) > 1:
        print("WARNING: multiple source model identifiers were explicitly allowed; review their family compatibility.")

    if args.check_only:
        print("Preflight successful. No data was staged, no weights were downloaded, and no training occurred.")
        return 0

    trainer_spec = TRAINER_SOURCES[family]
    trainer_path = TRAINER_CACHE / trainer_spec["filename"]
    if not trainer_path.is_file():
        parser.error(
            f"Official trainer is not cached: {trainer_path}. Run "
            "python ml/train_lora.py --fetch-official-trainers first; that download is explicit and hash-verified."
        )
    try:
        trainer_bytes = trainer_path.read_bytes()
    except OSError as exc:
        parser.error(f"Could not read verified trainer {trainer_path}: {exc}")
    if git_blob_sha(trainer_bytes) != trainer_spec["blob_sha"]:
        parser.error(f"Cached trainer failed integrity verification: {trainer_path}")

    try:
        import torch
        import diffusers
    except ImportError as exc:
        parser.error(
            "Training dependencies are missing. Install PyTorch for this machine first, then run "
            "python -m pip install -r requirements-training-lora.txt"
        )
    try:
        precision = choose_precision(torch, args.precision)
    except ValueError as exc:
        parser.error(str(exc))
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    staging_dir = STAGING_ROOT / f"run-{stamp}-{uuid.uuid4().hex[:8]}"
    try:
        train_dir, validation_dir, train_rows, validation_rows = prepare_imagefolder(
            examples, staging_dir, args.seed, args.validation_ratio
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    try:
        cuda_available = bool(torch.cuda.is_available())
        hardware: dict[str, Any] = {
            "device": "cuda" if cuda_available else "cpu",
            "torch_version": str(torch.__version__),
            "diffusers_version": str(diffusers.__version__),
            "cuda_available": cuda_available,
        }
        if cuda_available:
            props = torch.cuda.get_device_properties(0)
            hardware["gpu_name"] = props.name
            hardware["gpu_vram_bytes"] = int(props.total_memory)
            if family == "sdxl" and resolution >= 768 and props.total_memory < 12 * 1024**3:
                print("WARNING: SDXL at this resolution may exceed available VRAM on this GPU; try --resolution 512 if it runs out of memory.")
            elif family == "sd" and props.total_memory < 6 * 1024**3:
                print("WARNING: this GPU has limited VRAM for LoRA training; batch size 1 and gradient checkpointing are enabled.")
        else:
            print("WARNING: no CUDA GPU detected. CPU training may be extremely slow and memory-heavy; no timing estimate is assumed.")
        training_config = {
            "status": "prepared",
            "model": model_arg,
            "model_family": family,
            "model_path_is_local": local_model,
            "official_trainer": f"huggingface/diffusers@{TRAINER_VERSION}",
            "official_trainer_git_blob_sha": trainer_spec["blob_sha"],
            "source_model_identifiers": dict(source_models),
            "unknown_source_model_count": unknown_sources,
            "source_model_compatibility_confirmed_by_user": args.confirm_source_family,
            "dataset_count": len(examples),
            "training_count": len(train_rows),
            "validation_count": len(validation_rows),
            "skipped_manifest_rows": dict(skipped),
            "dataset_manifest_sha256": hashlib.sha256(
                "\n".join(f"{r['path']}\t{r['caption']}" for r in sorted(examples, key=lambda x: x["path"])).encode("utf-8")
            ).hexdigest(),
            "staging_directory": str(staging_dir),
            "hardware": hardware,
            "parameters": {
                "resolution": resolution,
                "train_batch_size": args.train_batch_size,
                "gradient_accumulation_steps": args.gradient_accumulation_steps,
                "max_train_steps": args.max_train_steps,
                "learning_rate": args.learning_rate,
                "rank": args.rank,
                "seed": args.seed,
                "precision": precision,
                "checkpointing_steps": args.checkpointing_steps,
                "validation_ratio": args.validation_ratio,
                "validation_prompt_provided": bool(args.validation_prompt),
            },
            "training_image_paths": [row["path"] for row in train_rows],
            "validation_image_paths": [row["path"] for row in validation_rows],
        }
        if args.resume_from_checkpoint:
            validate_resume_compatibility(output_dir, training_config)
        (output_dir / "training-config.json").write_text(
            json.dumps(training_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (output_dir / "training-manifest.json").write_text(
            json.dumps({
                "train": [{"path": row["path"], "caption_sha256": hashlib.sha256(row["caption"].encode("utf-8")).hexdigest()} for row in train_rows],
                "validation": [{"path": row["path"], "caption_sha256": hashlib.sha256(row["caption"].encode("utf-8")).hexdigest()} for row in validation_rows],
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        shutil.rmtree(staging_dir, ignore_errors=True)
        parser.error(f"Could not safely prepare/resume local training config: {exc}")

    command = [
        shutil.which("accelerate") or "accelerate", "launch",
        "--num_processes", "1",
        "--mixed_precision", precision,
        str(trainer_path),
        "--pretrained_model_name_or_path", model_arg,
        "--train_data_dir", str(train_dir),
        "--image_column", "image",
        "--caption_column", "text",
        "--resolution", str(resolution),
        "--center_crop",
        "--train_batch_size", str(args.train_batch_size),
        "--gradient_accumulation_steps", str(args.gradient_accumulation_steps),
        "--max_train_steps", str(args.max_train_steps),
        "--learning_rate", str(args.learning_rate),
        "--lr_scheduler", "constant",
        "--lr_warmup_steps", "0",
        "--output_dir", str(output_dir),
        "--checkpointing_steps", str(args.checkpointing_steps),
        "--checkpoints_total_limit", "3",
        "--rank", str(args.rank),
        "--seed", str(args.seed),
        "--dataloader_num_workers", "0",
        "--report_to", "tensorboard",
        "--gradient_checkpointing",
        "--mixed_precision", precision,
    ]
    if args.validation_prompt:
        command.extend(["--validation_prompt", args.validation_prompt])
    if args.resume_from_checkpoint:
        command.extend(["--resume_from_checkpoint", args.resume_from_checkpoint])

    environment = os.environ.copy()
    if args.allow_model_download:
        for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE"):
            environment.pop(key, None)
    else:
        environment.update({
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "DIFFUSERS_OFFLINE": "1",
        })
    training_config["status"] = "training"
    (output_dir / "training-config.json").write_text(
        json.dumps(training_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    training_log = output_dir / "training.log"
    print("Starting real training with the pinned official Diffusers script.")
    print("Remote model downloads are " + ("explicitly enabled." if args.allow_model_download else "disabled (local model/cache only)."))
    print(f"Local training log: {training_log}")
    trainer_process: subprocess.Popen[str] | None = None
    try:
        with training_log.open("a", encoding="utf-8") as log_handle:
            log_handle.write("\n=== Training attempt " + datetime.now(timezone.utc).isoformat() + " ===\n")
            log_handle.flush()
            trainer_process = subprocess.Popen(
                command,
                cwd=root,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            if trainer_process.stdout is None:
                raise RuntimeError("The training subprocess did not expose a readable output stream.")
            for line in trainer_process.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log_handle.write(line)
                log_handle.flush()
            trainer_process.wait()
        process = trainer_process
    except KeyboardInterrupt:
        if trainer_process is not None and trainer_process.poll() is None:
            trainer_process.terminate()
            try:
                trainer_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                trainer_process.kill()
                trainer_process.wait()
        training_config["status"] = "interrupted"
        (output_dir / "training-config.json").write_text(
            json.dumps(training_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Training interrupted. Existing checkpoints and training.log remain in {output_dir}.", file=sys.stderr)
        return 130
    except (OSError, RuntimeError) as exc:
        training_config["status"] = "failed_to_start"
        training_config["error"] = f"{type(exc).__name__}: {exc}"
        (output_dir / "training-config.json").write_text(
            json.dumps(training_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Could not start the trainer or save its logs: {exc}", file=sys.stderr)
        return 2

    result: dict[str, Any] = {
        "exit_code": process.returncode,
        "output_dir": str(output_dir),
        "status": "failed",
    }
    if process.returncode != 0:
        training_config["status"] = "failed"
        training_config["trainer_exit_code"] = process.returncode
    else:
        artifact = output_dir / "pytorch_lora_weights.safetensors"
        if not artifact.is_file() or artifact.stat().st_size <= 0:
            training_config["status"] = "failed_missing_lora_artifact"
            result["error"] = "Trainer exited successfully but pytorch_lora_weights.safetensors is missing or empty."
        else:
            try:
                from safetensors import safe_open
                with safe_open(str(artifact), framework="pt", device="cpu") as handle:
                    keys = list(handle.keys())
            except Exception as exc:
                training_config["status"] = "failed_invalid_lora_artifact"
                result["error"] = f"LoRA safetensors validation failed: {type(exc).__name__}: {exc}"
            else:
                if not keys or not any("lora" in key.lower() for key in keys):
                    training_config["status"] = "failed_invalid_lora_artifact"
                    result["error"] = "The output safetensors file has no recognizable LoRA keys."
                else:
                    training_config["status"] = "completed"
                    result.update({
                        "status": "completed",
                        "artifact": str(artifact),
                        "artifact_bytes": artifact.stat().st_size,
                        "tensor_key_count": len(keys),
                    })
    (output_dir / "training-config.json").write_text(
        json.dumps(training_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "training-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] == "completed":
        print(f"LoRA training completed and safetensors keys verified: {result['artifact']}")
        print(f"Artifact size: {result['artifact_bytes']} bytes; tensor keys: {result['tensor_key_count']}")
        print("Use this file as --lora in ml/generate_diffusion.py with the same compatible model family.")
        return 0
    print(f"Training did not produce a validated LoRA artifact. Inspect local logs/config in {output_dir}.", file=sys.stderr)
    if result.get("error"):
        print(result["error"], file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
