#!/usr/bin/env python3
"""Export only IMAGE's own from-scratch generator checkpoint to ONNX."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from networks import ConditionalGenerator

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/onnx")
    args = parser.parse_args()
    checkpoint_path = args.checkpoint if args.checkpoint.is_absolute() else ROOT / args.checkpoint
    if not checkpoint_path.is_file():
        parser.error(f"Checkpoint not found: {checkpoint_path}")
    # Use this only with checkpoints created by this project's own ml/train.py.
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if checkpoint.get("model_origin") != "random-initialization" or checkpoint.get("pretrained_checkpoint_used") is not False:
        parser.error("Refusing to export a checkpoint not marked as IMAGE's own from-scratch model.")
    vocab = checkpoint["vocab"]
    model = ConditionalGenerator(
        vocab,
        latent_dim=int(checkpoint["latent_dim"]),
        base_channels=int(checkpoint["generator_channels"]),
        image_channels=int(checkpoint.get("image_channels", 4)),
    )
    model.load_state_dict(checkpoint["generator_state_dict"])
    model.eval()

    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "image-anime-generator.onnx"
    noise = torch.zeros(1, int(checkpoint["latent_dim"]), dtype=torch.float32)
    labels = torch.zeros(1, len(checkpoint["attributes"]), dtype=torch.long)
    torch.onnx.export(
        model,
        (noise, labels),
        str(model_path),
        input_names=["noise", "labels"],
        output_names=["rgba"],
        dynamic_axes={"noise": {0: "batch"}, "labels": {0: "batch"}, "rgba": {0: "batch"}},
        opset_version=17,
        do_constant_folding=True,
        dynamo=False,
    )
    metadata = {
        "model_origin": "IMAGE-trained-from-random-initialization",
        "pretrained_checkpoint_used": False,
        "distillation_used": False,
        "image_size": checkpoint.get("image_size", [64, 96]),
        "image_channels": checkpoint.get("image_channels", 4),
        "latent_dim": checkpoint["latent_dim"],
        "attributes": checkpoint["attributes"],
        "vocab": vocab,
        "training_image_count": checkpoint.get("dataset_count"),
        "source_checkpoint": checkpoint_path.name,
        "onnx_file": model_path.name,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"ONNX model exported: {model_path}")
    print("Export success is not a memory benchmark; run ml/benchmark_onnx.py on the target PC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
