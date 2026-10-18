#!/usr/bin/env python3
"""Train a small conditional GAN from random initialization; no pretrained weights."""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageOps
from torch import nn
from torch.utils.data import DataLoader, Dataset

from networks import ATTRIBUTES, ConditionalDiscriminator, ConditionalGenerator

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SIZE = (64, 96)  # width, height
ELIGIBLE = {"approved"}


def load_approved_rows(csv_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            path = row.get("path", "").strip()
            if not path:
                continue
            flags = (row.get("visual_review", "").strip().lower(),
                     row.get("license_review", "").strip().lower(),
                     row.get("training_permission", "").strip().lower())
            if any(flag not in ELIGIBLE for flag in flags):
                continue
            if any(not row.get(attribute, "").strip() for attribute in ATTRIBUTES):
                continue
            absolute = (ROOT / path).resolve()
            if not absolute.is_relative_to(ROOT) or not absolute.is_file():
                continue
            row["_absolute_path"] = str(absolute)
            rows.append(row)
    return rows


def make_vocab(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    return {attribute: sorted({row[attribute].strip() for row in rows}) for attribute in ATTRIBUTES}


class CharacterDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], vocab: dict[str, list[str]]) -> None:
        self.rows = rows
        self.vocab = vocab
        self.maps = {attribute: {value: i for i, value in enumerate(vocab[attribute])} for attribute in ATTRIBUTES}

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.rows[index]
        with Image.open(row["_absolute_path"]) as source:
            image = source.convert("RGBA")
            fitted = ImageOps.contain(image, IMAGE_SIZE, method=Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
            x = (IMAGE_SIZE[0] - fitted.width) // 2
            y = (IMAGE_SIZE[1] - fitted.height) // 2
            canvas.alpha_composite(fitted, dest=(x, y))
            array = np.asarray(canvas, dtype=np.float32)
        pixels = torch.from_numpy(array.copy()).permute(2, 0, 1).contiguous()
        pixels = pixels.div(127.5).sub(1.0)
        labels = torch.tensor([self.maps[a][row[a].strip()] for a in ATTRIBUTES], dtype=torch.long)
        return pixels, labels


def save_sample_grid(generator: ConditionalGenerator, dataset: CharacterDataset, device: torch.device, latent_dim: int, output: Path, count: int = 16) -> None:
    generator.eval()
    picks = [dataset[i % len(dataset)][1] for i in range(count)]
    labels = torch.stack(picks).to(device)
    noise = torch.randn(count, latent_dim, device=device)
    with torch.no_grad():
        result = generator(noise, labels).detach().cpu().clamp(-1, 1)
    tile_w, tile_h = IMAGE_SIZE
    columns = 4
    rows = (count + columns - 1) // columns
    grid = Image.new("RGBA", (columns * tile_w, rows * tile_h), (232, 232, 232, 255))
    for i in range(count):
        array = ((result[i].permute(1, 2, 0) + 1.0) * 127.5).byte().numpy()
        tile = Image.fromarray(array, mode="RGBA")
        grid.alpha_composite(tile, dest=((i % columns) * tile_w, (i // columns) * tile_h))
    output.parent.mkdir(parents=True, exist_ok=True)
    grid.save(output)
    generator.train()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=ROOT / "data/training-labels.csv")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--max-images", type=int, default=100, help="Number of approved images for the pilot; use 0 to include all approved images")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--latent-dim", type=int, default=96)
    parser.add_argument("--generator-channels", type=int, default=128)
    parser.add_argument("--discriminator-channels", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0002)
    parser.add_argument("--save-every", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/training")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("--device cuda requested but CUDA is not available")
    device = torch.device("cuda" if args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available()) else "cpu")
    labels_path = args.labels if args.labels.is_absolute() else ROOT / args.labels
    rows = load_approved_rows(labels_path)
    if args.max_images < 0:
        parser.error("--max-images must be 0 (all approved) or a positive count")
    if args.max_images and len(rows) > args.max_images:
        rows = random.Random(args.seed).sample(rows, args.max_images)
    if len(rows) < 8:
        parser.error(
            f"Only {len(rows)} images pass visual_review, license_review and training_permission='approved' "
            "and have all required labels. Review data/training-labels.csv first; nothing has been trained."
        )
    vocab = make_vocab(rows)
    low_variation = [attribute for attribute in ATTRIBUTES if len(vocab[attribute]) < 2]
    if low_variation:
        print("WARNING: attributes with fewer than 2 values cannot meaningfully vary: " + ", ".join(low_variation))
    if len(rows) < 100:
        print(f"WARNING: training pilot has only {len(rows)} approved images; overfitting is likely.")

    dataset = CharacterDataset(rows, vocab)
    loader = DataLoader(dataset, batch_size=max(1, args.batch_size), shuffle=True, num_workers=0, drop_last=False)
    generator = ConditionalGenerator(vocab, latent_dim=args.latent_dim, base_channels=args.generator_channels).to(device)
    discriminator = ConditionalDiscriminator(vocab, base_channels=args.discriminator_channels).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer_g = torch.optim.Adam(generator.parameters(), lr=args.lr, betas=(0.5, 0.999))
    optimizer_d = torch.optim.Adam(discriminator.parameters(), lr=args.lr, betas=(0.5, 0.999))
    args.output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metadata: dict[str, Any] = {
        "model_origin": "random-initialization",
        "pretrained_checkpoint_used": False,
        "distillation_used": False,
        "dataset_count": len(rows),
        "image_size": list(IMAGE_SIZE),
        "image_channels": 4,
        "attributes": list(ATTRIBUTES),
        "vocab": vocab,
        "latent_dim": args.latent_dim,
        "generator_channels": args.generator_channels,
        "discriminator_channels": args.discriminator_channels,
        "seed": args.seed,
    }
    (args.output_dir / "training-config.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    for epoch in range(1, args.epochs + 1):
        generator.train()
        discriminator.train()
        losses_g: list[float] = []
        losses_d: list[float] = []
        for real, labels in loader:
            real = real.to(device)
            labels = labels.to(device)
            batch = real.shape[0]

            optimizer_d.zero_grad(set_to_none=True)
            real_logits = discriminator(real, labels)
            noise = torch.randn(batch, args.latent_dim, device=device)
            fake = generator(noise, labels).detach()
            fake_logits = discriminator(fake, labels)
            loss_d = criterion(real_logits, torch.full_like(real_logits, 0.9)) + criterion(fake_logits, torch.zeros_like(fake_logits))
            loss_d.backward()
            optimizer_d.step()

            optimizer_g.zero_grad(set_to_none=True)
            noise = torch.randn(batch, args.latent_dim, device=device)
            generated = generator(noise, labels)
            generated_logits = discriminator(generated, labels)
            loss_g = criterion(generated_logits, torch.ones_like(generated_logits))
            loss_g.backward()
            optimizer_g.step()

            losses_g.append(float(loss_g.detach().cpu()))
            losses_d.append(float(loss_d.detach().cpu()))

        if epoch == 1 or epoch % args.save_every == 0 or epoch == args.epochs:
            checkpoint = {
                **metadata,
                "epoch": epoch,
                "generator_state_dict": generator.state_dict(),
                "discriminator_state_dict": discriminator.state_dict(),
                "optimizer_g_state_dict": optimizer_g.state_dict(),
                "optimizer_d_state_dict": optimizer_d.state_dict(),
            }
            torch.save(checkpoint, args.output_dir / f"checkpoint-epoch-{epoch:04d}.pt")
            save_sample_grid(generator, dataset, device, args.latent_dim, args.output_dir / f"samples-epoch-{epoch:04d}.png")
            print(
                f"epoch={epoch}/{args.epochs} "
                f"loss_g={sum(losses_g)/max(1,len(losses_g)):.4f} "
                f"loss_d={sum(losses_d)/max(1,len(losses_d)):.4f}"
            )
    print(f"Training finished. Outputs written to {args.output_dir}")
    print("This is an experimental baseline, not a quality or 2 GB-memory guarantee.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
