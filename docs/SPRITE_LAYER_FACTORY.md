# Sprite-sheet and character-layer factory

This utility creates reusable PNGs from a sprite sheet or image grid with Pillow. It follows a regular grid or exact pixel coordinates, preserves existing alpha, optionally removes only a border-connected background color, centers crops on a standard canvas, and records hashes and source attribution.

## Split a regular grid

```powershell
python -m pip install -r requirements.txt
python scripts/split_sprite_sheet.py --input "references/pibra-hairstyles.png" --output "generated/local-preview/pibra" --grid 5x4 --category hair --prefix pibra-hair --canvas 512x512 --trim-alpha --source-url "https://your-source.example/reference" --license "user-owned"
```

Grid 5x4 means five columns and four rows (20 cells). Odd-sized sheets are divided without losing edge pixels. If the input already has transparency, its alpha channel is preserved. Add --key-color "#FFFFFF" --key-tolerance 12 only for a border-connected near-white background; isolated white details inside a sprite are preserved.

## Split by exact coordinates

Create a UTF-8 file such as boxes.json:

```json
{
  "assets": [
    { "id": "pibra-bob", "name": "Blunt bob", "category": "hair", "bbox": [0, 0, 512, 512] },
    { "id": "pibra-side-braid", "name": "Side braid", "category": "hair", "bbox": [512, 0, 512, 512] },
    { "id": "pibra-smile", "name": "Smile", "category": "expressions", "bbox": [0, 512, 512, 512] }
  ]
}
```

Then run:

```powershell
python scripts/split_sprite_sheet.py --input "references/pibra-sheet.png" --output "generated/local-preview/pibra" --boxes-json "boxes.json" --canvas 512x512 --trim-alpha
```

Each bbox is [x, y, width, height] from the top-left. Coordinates must fit inside the source. IDs become safe lowercase filenames; duplicate IDs are rejected.

## Output

- hair/<id>.png, expressions/<id>.png, etc. — RGBA PNGs with the same canvas dimensions.
- contact-sheet.png — checkerboard preview to inspect transparency.
- manifest.json — source SHA-256, optional source URL/license/credit, boxes, output hashes, dimensions and processing settings.

Existing outputs are never silently overwritten. Use --overwrite only when intentionally replacing them. The input is never modified.

## Publish reviewed results on a feature branch

After reviewing the contact sheet and manifest, the optional PyGithub uploader can commit the output folder to an existing non-default branch:

```powershell
python -m pip install -r requirements-publish.txt
$env:GITHUB_TOKEN = "github_pat_..." # Set locally; never paste it into source control or chat.
python scripts/publish_character_layers.py --repo rikosama473-sketch/image --branch work/sprite-layer-factory-2026-10-20 --asset-dir "generated/local-preview/pibra" --character-id pibara
```

The publisher refuses the default branch, rejects symlinks, unsupported files and unsafe paths, checks destination collisions, and enforces conservative size limits. It never prints the token and does not create or merge a PR.

## Identity and licensing guardrails

- Cropping does not guarantee semantic isolation. A full character crop is still a whole-character image even if saved under a "hair" folder. Only call an image a hair/eye/accessory layer when the source and coordinates actually isolate it.
- This deterministic tool cannot invent hairstyles or separate overlapping pixels; use an identity-preserving generation workflow to create visual variants, then review them.
- Keep Pibara, Sunna and Chie references separate. Do not reuse Pibara's confirmed image for another character.
- Do not scrape and commit random web images without checking redistribution/modification permissions. Use the existing curated downloader (scripts/fetch_asset_packs.py) for allowlisted sources.
- Assets produced by an AI workflow still need visual identity review before production use.
