"""Safe anime-character prompt defaults for IMAGE's local CPU-oriented creator."""
from __future__ import annotations

RECOMMENDED_MODEL_ID = "hakurei/waifu-diffusion"
RECOMMENDED_MODEL_REVISION = "main"
RECOMMENDED_MODEL_VARIANT = "fp16"

BASE_NEGATIVE_PROMPT = (
    "lowres, blurry, worst quality, low quality, bad anatomy, bad hands, "
    "extra fingers, missing fingers, fused fingers, extra limbs, bad proportions, "
    "deformed face, crossed eyes, distorted mouth"
)
CHARACTER_ONLY_NEGATIVE_PROMPT = (
    "multiple people, 2girls, 2boys, duplicate character, extra head, "
    "character sheet, multiple views, collage, split screen, background, scenery, "
    "aura, particles, emojis, stickers, text, watermark, logo, signature, "
    "unrelated props"
)
CHARACTER_PROMPT_SUFFIX = (
    "solo, one anime character, full body, centered, clean anime line art, "
    "coherent proportions, clear face, visible clothing"
)
WHITE_BACKGROUND_PROMPT_SUFFIX = (
    "isolated character, plain white background, no scenery"
)


def build_generation_prompts(
    user_prompt: str,
    user_negative_prompt: str = "",
    character_mode: bool = True,
    transparent_background: bool = True,
) -> tuple[str, str]:
    """Compose positive/negative prompts while keeping built-in blocks additive."""
    if not isinstance(user_prompt, str) or not user_prompt.strip():
        raise ValueError("Escribe una descripción del personaje.")
    if not isinstance(user_negative_prompt, str):
        raise ValueError("Los negativos adicionales deben ser texto.")
    positive = [user_prompt.strip()]
    negative = [BASE_NEGATIVE_PROMPT]
    if character_mode:
        positive.append(CHARACTER_PROMPT_SUFFIX)
        negative.append(CHARACTER_ONLY_NEGATIVE_PROMPT)
    if transparent_background:
        # Diffusion doesn't reliably emit alpha; segment the white background locally.
        positive.append(WHITE_BACKGROUND_PROMPT_SUFFIX)
    if user_negative_prompt.strip():
        negative.append(user_negative_prompt.strip())
    return ", ".join(positive), ", ".join(negative)
