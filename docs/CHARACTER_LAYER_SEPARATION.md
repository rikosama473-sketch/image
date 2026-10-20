# Character layer separation: Pibara pilot

This pipeline turns the source illustration and its five existing hairstyle renders into aligned, transparent PNG layer candidates. It **does not** claim that an AI mask is pixel-perfect. Every extracted part is flagged for visual review before use in the character editor.

## Assets it creates

All PNGs preserve the source canvas dimensions and coordinates so the character does not jump when layers are switched:

- `model/whole-character.png`: full character cutout with transparent background.
- `model/head-face-candidate.png`: candidate head/face/hair/headwear mask.
- `model/body-without-head-candidate.png`: the original foreground minus a dilated head mask, for inspection and manual edge repair.
- `model/face-candidate.png`: semantic face-class candidate.
- `model/outfit-candidate.png`: clothing/accessory classes detected by the segmentation model.
- `hair/base-hair-candidate.png`: candidate hair layer from the source.
- `hair/variants/<id>.png`: hair mask candidate from each of the five existing variants.
- `hair/edit-delta/<id>-delta-candidate.png`: diagnostic pixels changed between the source and generated render in the upper 48% of the canvas. This is **not** a full hairstyle and is never substituted for a semantic hair mask unless that mask is nearly empty.
- `contact-sheet.png`: quick review sheet.
- `manifest.json`: source and output hashes, dimensions, model identifiers, coverage ratios, exact asset paths and warnings.

The `body-without-head-candidate` is an initial cut, not yet a seamless game-ready body plate. It may retain missed hair/face pixels or remove neck strands. A clean interchangeable model requires painting/reconstructing pixels hidden by the original head, shoulders or hair. Segmentation cannot recover pixels that were never visible.

## Rebuild locally

Use Python 3.10+ and enough memory for CPU inference. The first run downloads the foreground and semantic segmentation weights.

~~~bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch
python -m pip install -r requirements-character-layers.txt
python scripts/build_character_layers.py \
  --root . \
  --character pibara \
  --source from-PixAI-2034984086876227343-0.png \
  --variant blunt-bob=generated/character-assets/pibara/2026-10-20/run-39427500253/renders/01-blunt-bob.png \
  --variant long-straight=generated/character-assets/pibara/2026-10-20/run-39427500253/renders/02-long-straight.png \
  --variant high-ponytail=generated/character-assets/pibara/2026-10-20/run-39427500253/renders/03-high-ponytail.png \
  --variant twin-tails=generated/character-assets/pibara/2026-10-20/run-39445227631/renders/04-twin-tails.png \
  --variant side-braid=generated/character-assets/pibara/2026-10-20/run-39445227631/renders/05-side-braid.png \
  --output generated/character-layers/pibara/local-run
~~~

## Automated build

The workflow `.github/workflows/build-character-layers.yml` runs on pushes to the one pilot branch `work/character-layer-separation-2026-10`. It creates a versioned asset directory and commits generated candidates to that same branch if the runner has repository write permission. It never changes or removes the original source or the earlier render files.

## Model caveats

- Foreground removal uses `rembg`/U²-Net.
- Semantic parsing uses `mattmdjaga/segformer_b2_clothes`, a general clothing/people parser, not a model trained specifically on anime. It may miss strands, highlights, facial line art, non-human styling, and accessories.
- The difference fallback is a diagnostic patch only. It can contain unintended edits and is not evidence of a hair-only region.
- This pilot targets Pibara because that source reference is confirmed in the registry. Chie and Sunna remain without confirmed source images in `data/character-prompt-registry.json`; the workflow must not silently reuse Pibara's image for either.
- Keep all results in `candidate_requires_visual_review` until a human has reviewed the composited layers at full resolution.
