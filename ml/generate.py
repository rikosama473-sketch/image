#!/usr/bin/env python3
"""Generate PNG character samples from a checkpoint trained by ml/train.py."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from networks import ATTRIBUTES, ConditionalGenerator

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--hair", required=True)
    parser.add_argument("--clothing", required=True)
    parser.add_argument("--legs", required=True)
    parser.add_argument("--pose", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/generated")
    args = parser.parse_args()

    checkpoint_path = args.checkpoint if args.checkpoint.is_absolute() else ROOT / args.checkpoint
    if not checkpoint_path.is_file():
        parser.error(f"Checkpoint not found: {checkpoint_path}. Train the own model first.")
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("--device cuda requested but CUDA is not available")
    device = torch.device("cuda" if args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available()) else "cpu")
    # weights_only=False is only for the project's own checkpoint metadata/state dict.
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    vocab = checkpoint["vocab"]
    selections = {
        "hair": args.hair,
        "clothing": args.clothing,
        "legs": args.legs,
        "pose": args.pose,
        "background": args.background,
    }
    label_values: list[int] = []
    for attribute in ATTRIBUTES:
        value = selections[attribute]
        if value not in vocab.get(attribute, []):
            parser.error(f"Unknown {attribute} value {value!r}; choose one of: {', '.join(vocab.get(attribute, []))}")
        label_values.append(vocab[attribute].index(value))

    model = ConditionalGenerator(
        vocab,
        latent_dim=int(checkpoint["latent_dim"]),
        base_channels=int(checkpoint["generator_channels"]),
        image_channels=int(checkpoint.get("image_channels", 4)),
    ).to(device)
    model.load_state_dict(checkpoint["generator_state_dict"])
    model.eval()
    generator = torch.Generator(device=device)
    generator.manual_seed(args.seed)
    args.output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    args.output_dir.mkdir(parents=True, exist_ok=True)
    labels = torch.tensor([label_values] * args.count, dtype=torch.long, device=device)
    noise = torch.randn(args.count, int(checkpoint["latent_dim"]), generator=generator, device=device)
    with torch.no_grad():
        samples = model(noise, labels).cpu().clamp(-1, 1)
    for index, tensor in enumerate(samples):
        pixels = ((tensor.permute(1, 2, 0) + 1.0) * 127.5).byte().numpy()
        image = Image.fromarray(pixels, mode="RGBA")
        image.save(args.output_dir / f"anime-{args.seed}-{index + 1:03d}.png")
    print(f"Saved {args.count} images to {args.output_dir}")
    print("Transparency quality depends on alpha-channel examples in the training dataset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
