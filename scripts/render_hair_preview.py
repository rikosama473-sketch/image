from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "12.png"
HAIR = ROOT / "assets" / "parts" / "hair" / "cabello_01.svg"
OUT_DIR = ROOT / "preview-output"
OUT_FILE = OUT_DIR / "cabello_01-personaje-preview.png"


def main() -> int:
    if not SOURCE.is_file() or not HAIR.is_file():
        raise SystemExit("Falta 12.png o assets/parts/hair/cabello_01.svg; no se generó la previsualización.")
    base = Image.open(SOURCE).convert("RGBA")
    svg_bytes = cairosvg.svg2png(
        bytestring=HAIR.read_bytes(),
        output_width=base.width,
        output_height=base.height,
    )
    hair_layer = Image.open(io.BytesIO(svg_bytes)).convert("RGBA")
    if hair_layer.size != base.size:
        raise SystemExit(f"El lienzo del cabello no coincide: base={base.size}; overlay={hair_layer.size}")
    composite = Image.alpha_composite(base, hair_layer)
    # Provide a focused portrait preview instead of repeating the full-body reference.
    left, top, right, bottom = 155, 0, 660, 350
    preview = composite.crop((left, top, right, bottom))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preview.save(OUT_FILE, format="PNG", optimize=True)
    print(f"Preview written: {OUT_FILE} ({preview.width}x{preview.height})")
    print("Source preserved: 12.png was only read; the overlay was composited to a new file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
