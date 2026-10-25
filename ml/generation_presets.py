"""Safe anime-character prompt defaults for IMAGE's local CPU-oriented creator."""
from __future__ import annotations

RECOMMENDED_MODEL_ID = "hakurei/waifu-diffusion"

BASE_NEGATIVE_PROMPT = (
    "worst quality, low quality, lowres, blurry, jpeg artifacts, noisy image, "
    "bad anatomy, bad proportions, deformed body, malformed hands, bad hands, "
    "extra fingers, missing fingers, fused fingers, too many fingers, "
    "extra arms, missing arms, extra legs, missing legs, twisted limbs, "
    "deformed face, asymmetrical eyes, crossed eyes, uneven pupils, "
    "duplicated facial features, distorted mouth, unnatural joints"
)
CHARACTER_ONLY_NEGATIVE_PROMPT = (
    "multiple people, multiple characters, crowd, group, duplicate character, "
    "extra person, multiple heads, extra head, extra face, extra body, "
    "character sheet, multiple views, collage, split screen, panels, "
    "scenery, landscape, room, city, street, forest, architecture, detailed background, "
    "aura, glowing aura, magical effects, particles, floating symbols, "
    "emojis, stickers, text, watermark, logo, signature, border, speech bubble, "
    "UI elements, unrelated props outside the character"
)
CHARACTER_PROMPT_SUFFIX = (
    "one single anime character, one subject only, centered composition, "
    "full-body character design, entire character visible from head to feet, "
    "coherent anatomy and proportions, natural readable pose, clean anime line art, "
    "clear hair strands, clearly defined eyes and mouth, clothing design visible"
)
WHITE_BACKGROUND_PROMPT_SUFFIX = (
    "isolated single subject on a plain pure white background, no scenery, "
    "clean silhouette and clear separation from background for local transparent cutout"
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
