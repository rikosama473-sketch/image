"""Small conditional generator/discriminator initialized from random weights.

This baseline is intentionally tiny and low-resolution. It is not a pretrained
diffusion model and does not download weights. Quality is not guaranteed.
"""
from __future__ import annotations

from collections.abc import Mapping

import torch
from torch import nn

ATTRIBUTES = ("hair", "clothing", "legs", "pose", "background")
IMAGE_HEIGHT = 96
IMAGE_WIDTH = 64
IMAGE_CHANNELS = 4  # RGBA; opaque training images still teach opaque backgrounds.


def _condition_sizes(vocab: Mapping[str, list[str]]) -> list[int]:
    sizes = []
    for attribute in ATTRIBUTES:
        options = vocab.get(attribute, [])
        if not options:
            raise ValueError(f"Vocabulary has no categories for required attribute: {attribute}")
        sizes.append(len(options))
    return sizes


class ConditionalGenerator(nn.Module):
    def __init__(
        self,
        vocab: Mapping[str, list[str]],
        latent_dim: int = 96,
        base_channels: int = 128,
        embedding_dim: int = 8,
        image_channels: int = IMAGE_CHANNELS,
    ) -> None:
        super().__init__()
        self.latent_dim = latent_dim
        self.base_channels = base_channels
        self.image_channels = image_channels
        sizes = _condition_sizes(vocab)
        self.embeddings = nn.ModuleList([nn.Embedding(size, embedding_dim) for size in sizes])
        condition_dim = len(ATTRIBUTES) * embedding_dim
        self.project = nn.Linear(latent_dim + condition_dim, base_channels * 6 * 4)
        self.network = nn.Sequential(
            nn.Upsample(scale_factor=2, mode="nearest"),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode="nearest"),
            nn.Conv2d(base_channels, base_channels // 2, 3, padding=1),
            nn.BatchNorm2d(base_channels // 2),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode="nearest"),
            nn.Conv2d(base_channels // 2, base_channels // 4, 3, padding=1),
            nn.BatchNorm2d(base_channels // 4),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode="nearest"),
            nn.Conv2d(base_channels // 4, base_channels // 8, 3, padding=1),
            nn.BatchNorm2d(base_channels // 8),
            nn.ReLU(True),
            nn.Conv2d(base_channels // 8, image_channels, 3, padding=1),
            nn.Tanh(),
        )

    def _embed(self, labels: torch.Tensor) -> torch.Tensor:
        if labels.ndim != 2 or labels.shape[1] != len(ATTRIBUTES):
            raise ValueError(f"labels must have shape [batch, {len(ATTRIBUTES)}]")
        return torch.cat([embedding(labels[:, i]) for i, embedding in enumerate(self.embeddings)], dim=1)

    def forward(self, noise: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        conditioned = torch.cat([noise, self._embed(labels)], dim=1)
        features = self.project(conditioned).view(-1, self.base_channels, 6, 4)
        return self.network(features)


class ConditionalDiscriminator(nn.Module):
    def __init__(
        self,
        vocab: Mapping[str, list[str]],
        base_channels: int = 64,
        embedding_dim: int = 8,
        image_channels: int = IMAGE_CHANNELS,
    ) -> None:
        super().__init__()
        sizes = _condition_sizes(vocab)
        self.embeddings = nn.ModuleList([nn.Embedding(size, embedding_dim) for size in sizes])
        condition_dim = len(ATTRIBUTES) * embedding_dim
        self.features = nn.Sequential(
            nn.Conv2d(image_channels + condition_dim, base_channels, 4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_channels, base_channels * 2, 4, stride=2, padding=1),
            nn.BatchNorm2d(base_channels * 2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_channels * 2, base_channels * 4, 4, stride=2, padding=1),
            nn.BatchNorm2d(base_channels * 4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_channels * 4, base_channels * 8, 4, stride=2, padding=1),
            nn.BatchNorm2d(base_channels * 8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.output = nn.Linear(base_channels * 8, 1)

    def forward(self, image: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        embedded = torch.cat(
            [embedding(labels[:, i]) for i, embedding in enumerate(self.embeddings)],
            dim=1,
        )
        batch, _, height, width = image.shape
        condition_map = embedded[:, :, None, None].expand(batch, embedded.shape[1], height, width)
        features = self.features(torch.cat([image, condition_map], dim=1)).flatten(1)
        return self.output(features).squeeze(1)
