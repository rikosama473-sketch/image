# Character asset generation without an API key

This workflow creates character-specific image variants from references already stored in IMAGE, using the public Gradio API for Krea 2 Identity Edit. It does not require an OpenAI API key.

## First batch: Pibara hairstyles

Open Actions, select Generate character assets without an API key, and run the workflow with:

- Character: pibara
- Reference image: from-PixAI-2034984086876227343-0.png
- Asset pack: hair-core-5
- Background: transparent
- Base seed: 1201

The hair pack generates five edits: blunt bob, long straight, high ponytail, twin tails and side braid. Each instruction asks the editor to preserve Pibara's face, eye color, original hair color, accessories, line art, clothes, pose and background while changing only the hairstyle.

## Other packs

- expressions-core-5: happy, surprised, sad, annoyed and shy expressions.
- eyes-4: detail-only eye-rendering variants that keep the original iris color.
- accessories-4: one added ribbon, hair clip, star pin or headband per image.
- face-details-4: light freckles, one beauty mark, soft blush or subtle lower eyeliner.

The eye, accessory and face-detail packs are creative alternatives, not claims that the new traits are canonical.

## Output structure

Files are written beneath generated/character-assets/<character>/<date>/run-<run-id>/:

- renders/: full edited PNGs.
- transparent/: additional transparent PNG cutouts, if requested.
- contact-sheet.jpg: quick contact sheet.
- manifest.json: immutable source reference, source SHA-256, exact prompts, seeds, output hashes, dimensions and settings.
- PROMPTS.md: a readable record of every prompt used.

The character registry records the run, but the canonical prompt is not overwritten. Every batch remains marked as requiring visual identity review. Background removal is automated and may leave imperfect hair edges; do not treat the cutout as pixel-perfect masking.

## Chie and Sunna

The existing registry does not yet have canonical image paths assigned to Chie or Sunna. When generating those characters, set the exact reference image path in the workflow input. Do not leave the Pibara default reference selected for another character.

## Cost, privacy and availability

This workflow does not use the OpenAI API or an OpenAI API key. It submits the selected source image as a public URL to a third-party Hugging Face Space. Its queue, compute quota, availability, terms and privacy practices are controlled by that service. Do not send images there unless they are appropriate for third-party processing. If the Space is unavailable or rate-limited, the run fails and no generated-image PR should be created. Original references are never edited or overwritten.
