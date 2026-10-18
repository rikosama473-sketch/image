#!/usr/bin/env python3
"""Generate samples using CPU ONNX Runtime, without importing PyTorch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=ROOT / "outputs/onnx")
    parser.add_argument("--hair", required=True)
    parser.add_argument("--clothing", required=True)
    parser.add_argument("--legs", required=True)
    parser.add_argument("--pose", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/generated-onnx")
    args = parser.parse_args()

    model_dir = args.model_dir if args.model_dir.is_absolute() else ROOT / args.model_dir
    model_path = model_dir / "image-anime-generator.onnx"
    metadata_path = model_dir / "metadata.json"
    if not model_path.is_file() or not metadata_path.is_file():
        parser.error(f"ONNX model/metadata not found in {model_dir}; train and export the own model first.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("model_origin") != "IMAGE-trained-from-random-initialization" or metadata.get("pretrained_checkpoint_used") is not False:
        parser.error("Model metadata does not identify IMAGE's own from-scratch generator.")

    chosen = {"hair": args.hair, "clothing": args.clothing, "legs": args.legs, "pose": args.pose, "background": args.background}
    attributes = metadata["attributes"]
    vocab = metadata["vocab"]
    label_values = []
    for attribute in attributes:
        value = chosen.get(attribute)
        if value not in vocab.get(attribute, []):
            parser.error(f"Unknown {attribute} value {value!r}. Valid values: {', '.join(vocab.get(attribute, []))}")
        label_values.append(vocab[attribute].index(value))

    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.enable_mem_pattern = True
    session = ort.InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(args.seed)
    noise = rng.standard_normal((args.count, int(metadata["latent_dim"])), dtype=np.float32)
    labels = np.tile(np.asarray(label_values, dtype=np.int64), (args.count, 1))
    result = session.run(["rgba"], {"noise": noise, "labels": labels})[0]
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    height, width = int(metadata["image_size"][1]), int(metadata["image_size"][0])
    for index, sample in enumerate(result):
        # Convert CHW[-1, 1] to uint8 RGBA, then save as a standard PNG.
        pixels = np.clip((np.transpose(sample, (1, 2, 0)) + 1.0) * 127.5, 0, 255).astype(np.uint8)
        if pixels.shape[:2] != (height, width):
            raise RuntimeError(f"Unexpected output resolution: {pixels.shape}")
        Image.fromarray(pixels, mode="RGBA").save(out_dir / f"anime-{args.seed}-{index + 1:03d}.png")
    print(f"Saved {args.count} sample(s) to {out_dir}")
    print("Measure peak memory with ml/benchmark_onnx.py; transparency depends on alpha quality in training data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
