#!/usr/bin/env python3
"""Generate hairstyle variants from a public image already stored in this repository."""
from __future__ import annotations
import base64, hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageOps

API_URL = "https://api.openai.com/v1/images/edits"
MODEL = "gpt-image-2.5-sunburst"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
STYLE_PACKS = {
    "core-5": [
        ("blunt-bob", "a neat blunt bob ending at the chin, smooth rounded silhouette, clearly defined ends"),
        ("long-straight", "long straight hair falling below the shoulders, smooth strands and a clean silhouette"),
        ("high-ponytail", "a high ponytail tied at the crown, flowing length and a few restrained framing strands"),
        ("twin-tails", "balanced twin tails tied on both sides, matching volume and length"),
        ("side-braid", "one substantial side braid resting over one shoulder, visible woven strands"),
    ],
    "core-6": [
        ("blunt-bob", "a neat blunt bob ending at the chin, smooth rounded silhouette, clearly defined ends"),
        ("long-straight", "long straight hair falling below the shoulders, smooth strands and a clean silhouette"),
        ("high-ponytail", "a high ponytail tied at the crown, flowing length and a few restrained framing strands"),
        ("twin-tails", "balanced twin tails tied on both sides, matching volume and length"),
        ("side-braid", "one substantial side braid resting over one shoulder, visible woven strands"),
        ("layered-waves", "shoulder-length layered hair with soft loose waves and controlled volume"),
    ],
    "short-cuts": [
        ("pixie-cut", "a tidy short pixie cut, close at the sides with a textured top"),
        ("chin-bob", "a rounded chin-length bob with clearly defined ends"),
        ("asymmetric-bob", "an asymmetrical bob, one side modestly longer than the other"),
        ("shag-cut", "a layered shag haircut with separated feathered tips"),
        ("wolf-cut", "a stylized medium-short wolf cut with crown volume and layered ends"),
        ("pageboy-cut", "a smooth classic pageboy cut with a curved outline and neat fringe"),
    ],
    "updos": [
        ("high-bun", "a compact high bun with visible wrapped strands"),
        ("low-bun", "a low nape bun with a few neat framing strands"),
        ("half-up", "a half-up hairstyle with the upper section tied back and the rest loose"),
        ("twin-buns", "two balanced buns high on either side, clean and clearly defined"),
        ("high-ponytail", "a high ponytail with a clear tie point and flowing length"),
        ("braided-crown", "a crown braid following the top of the head, with the remaining hair gathered neatly"),
    ],
    "bangs": [
        ("blunt-bangs", "straight blunt bangs across the forehead, even and clearly separated"),
        ("side-swept-bangs", "side-swept bangs flowing diagonally across the forehead"),
        ("curtain-bangs", "curtain bangs parted at the center and framing both sides of the face"),
        ("wispy-bangs", "light wispy bangs with fine separated locks"),
        ("middle-part", "a clean middle part with balanced face-framing locks and no heavy fringe"),
        ("deep-side-part", "a deep side part with a sweeping, clearly visible hair direction"),
    ],
    "waves-braids": [
        ("loose-waves", "long loose waves with readable S-shaped strands"),
        ("defined-curls", "defined springy curls with consistent curl size and separated strands"),
        ("side-braid", "a defined side braid with visible woven sections"),
        ("fishtail-braid", "a long fishtail braid with a clear herringbone pattern"),
        ("double-braids", "two neat braids, one on each side, with matching thickness"),
        ("layered-waves", "medium-length layered waves with varied but controlled volume"),
    ],
}
BASE_INSTRUCTIONS = (
    "This is a precise edit of the existing supplied character image, not a new character design or an illustration inspired by it. "
    "Change ONLY the hairstyle and arrangement of the hair as requested. Preserve the exact recognizable face, eye shape and color, "
    "glasses, headband and other visible accessories, expression, skin tone, head proportions, hair color, original line-art weight, "
    "shading, color palette, brush/finish, background, crop and all other visible details. Do not add, remove or redesign accessories. "
    "Do not change clothing or invent clothing that is not visible. Do not change the pose or camera framing. Do not beautify, simplify, "
    "redraw in another anime style, add characters, text, logos or watermarks. Do not recrop or resize the face. The requested hair shape, "
    "parting, strand direction, volume and ends are the ONLY intended change. Preserve non-hair regions as closely as possible."
)

def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(1)

def safe_source_path(raw_path, root):
    raw_path = raw_path.strip()
    posix = PurePosixPath(raw_path)
    if not raw_path or posix.is_absolute() or ".." in posix.parts:
        fail("reference_image must be a repository-relative path without '..'.")
    if posix.suffix.lower() not in ALLOWED_EXTENSIONS:
        fail("Use a PNG, JPG/JPEG or WebP reference.")
    path = (root / Path(*posix.parts)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        fail("reference_image resolves outside the repository.")
    if not path.is_file():
        fail("Reference image was not found in this checked-out revision: " + raw_path)
    if path.stat().st_size > 20 * 1024 * 1024:
        fail("Reference image exceeds 20 MiB; choose a smaller source.")
    return path

def extract_embedded_prompt(image_path, root):
    # Reuse IMAGE's established metadata extractor first so nested JSON/PNG workflow
    # metadata and common diffusion parameter blocks are parsed consistently.
    try:
        import importlib.util
        extractor_path = root / "scripts" / "extract_generation_metadata.py"
        spec = importlib.util.spec_from_file_location("image_source_metadata_extractor", extractor_path)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            row = module.extract_one(image_path, root)
            prompt = str(row.get("prompt", "") or "").strip()[:30000]
            keys = [item.strip() for item in str(row.get("metadata_keys", "")).split(";") if item.strip()]
            return prompt, keys
    except Exception:
        pass
    # Defensive fallback if the shared extractor cannot be loaded.
    try:
        with Image.open(image_path) as im:
            info = dict(im.info)
        keys = sorted(str(k) for k in info)
        for candidate in ("prompt", "Prompt", "parameters", "Parameters", "Description", "Comment"):
            value = info.get(candidate)
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            if isinstance(value, str) and value.strip():
                return value.strip()[:30000], keys
        return "", keys
    except Exception:
        return "", []

def prepare_head_reference(source_path, target_path, height_ratio=0.70):
    """Crop a user-reviewable upper-head region; do not guess that a narrow band contains the full face."""
    try:
        height_ratio = float(height_ratio)
    except (TypeError, ValueError):
        fail("HEAD_CROP_HEIGHT_RATIO must be numeric.")
    if not 0.55 <= height_ratio <= 0.90:
        fail("HEAD_CROP_HEIGHT_RATIO must be between 0.55 and 0.90.")
    with Image.open(source_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    width, height = image.size
    left = int(round(width * 0.02))
    right = int(round(width * 0.98))
    # A crop height of only 28% of a full-length portrait often cuts the chin/face.
    # This ratio deliberately keeps more head and hair, and can be previewed before paid generation.
    bottom = min(int(round(width * height_ratio)), int(round(height * 0.75)))
    if right - left < 256 or bottom < 200:
        fail("Could not prepare a useful head crop; choose a larger upright image.")
    crop_box = [left, 0, right, bottom]
    head = image.crop(tuple(crop_box))
    max_w, max_h = 960, 920
    scale = min(max_w / head.width, max_h / head.height)
    resized = head.resize(
        (max(1, int(round(head.width * scale))), max(1, int(round(head.height * scale)))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", (1024, 1024), "white")
    canvas.paste(resized, ((1024 - resized.width) // 2, 32))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target_path, format="PNG", optimize=True)
    png_bytes = target_path.read_bytes()
    data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode("ascii")
    return data_url, {
        "crop_box_pixels": crop_box,
        "source_crop_dimensions": [right - left, bottom],
        "api_input_dimensions": [1024, 1024],
        "height_ratio": height_ratio,
        "crop_method": "top head zone with configurable height ratio; inspect the preview before paid generation",
    }


def infer_visual_base_prompt(head_data_url, requests):
    """Infer a reusable identity prompt from the cropped reference, not the original generation prompt."""
    payload = {
        "model": "gpt-6-luna",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Describe an illustrated character for reusable image generation. Treat the image as a cropped "
                    "identity reference. Do not name a character, franchise, LoRA, checkpoint, or claim this is the "
                    "original generation prompt. Return only stable traits that should remain across hairstyle variants: "
                    "visible facial features, eye color, glasses or head accessories, hair color (not haircut or length), "
                    "color palette, line art and shading. Exclude hairstyle shape, length, fringe, parting, braids, ponytails "
                    "and updos because these will be changed. Do not invent unseen details. Return a concise prompt in English "
                    "as JSON with keys visual_base_prompt (string), stable_traits (array of strings), uncertainties (array of strings)."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Build a stable identity description from this cropped head reference. Exclude the hairstyle itself."},
                    {"type": "image_url", "image_url": {"url": head_data_url, "detail": "high"}},
                ],
            },
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": 900,
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"},
            json=payload,
            timeout=(30, 180),
        )
    except requests.RequestException as exc:
        fail("Visual prompt extraction request failed: " + str(exc))
    if not response.ok:
        fail("Vision API returned HTTP " + str(response.status_code) + ": " + response.text[:1400])
    try:
        raw = response.json()["choices"][0]["message"]["content"]
        result = json.loads(raw)
        base_prompt = str(result.get("visual_base_prompt", "")).strip()
        if not base_prompt:
            fail("Vision analysis returned an empty visual_base_prompt.")
        return {
            "model": "gpt-6-luna",
            "visual_base_prompt": base_prompt[:8000],
            "stable_traits": [str(item)[:300] for item in result.get("stable_traits", [])[:30]],
            "uncertainties": [str(item)[:500] for item in result.get("uncertainties", [])[:20]],
            "is_original_generation_prompt": False,
            "review_status": "needs_manual_review",
        }
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        fail("Could not parse the visual prompt response as JSON: " + str(exc))


def render_contact_sheet(image_paths, target):
    columns, cell_w, image_h, label_h, margin = 3, 400, 560, 48, 18
    rows = (len(image_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w + (columns + 1) * margin,
                              rows * (image_h + label_h) + (rows + 1) * margin), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for i, (label, path) in enumerate(image_paths):
        with Image.open(path) as im:
            thumb = ImageOps.contain(im.convert("RGB"), (cell_w, image_h), Image.Resampling.LANCZOS)
        row, col = divmod(i, columns)
        x = margin + col * (cell_w + margin)
        y = margin + row * (image_h + label_h + margin)
        sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + (image_h - thumb.height) // 2))
        draw.rectangle((x, y + image_h, x + cell_w, y + image_h + label_h), fill="#f1f1f1")
        draw.text((x + 12, y + image_h + 12), label.replace("-", " "), fill="#202020", font=font)
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="JPEG", quality=90, optimize=True, progressive=True)

def main():
    import requests
    generation_mode = os.environ.get("GENERATION_MODE", "generate").strip().lower()
    if generation_mode not in {"preview", "generate"}:
        fail("GENERATION_MODE must be preview or generate.")
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if generation_mode == "generate" and not api_key:
        fail("Missing Actions secret OPENAI_API_KEY. Never put the API key in source code.")
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    commit_sha = os.environ.get("GITHUB_SHA", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    character_id = os.environ.get("CHARACTER_ID", "").strip().lower()
    style_pack = os.environ.get("STYLE_PACK", "core-6").strip().lower()
    head_crop_height_ratio = os.environ.get("HEAD_CROP_HEIGHT_RATIO", "0.70").strip()
    raw_source = os.environ.get("REFERENCE_IMAGE", "").strip()
    root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", character_id):
        fail("CHARACTER_ID must be a lowercase id such as pibara, chie, sunna, personaje-4 or personaje-5.")
    if style_pack not in STYLE_PACKS:
        fail("Unknown style pack: " + style_pack)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not commit_sha:
        fail("Missing GitHub repository context; run this script through GitHub Actions.")
    source_path = safe_source_path(raw_source, root)
    source_bytes = source_path.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    try:
        with Image.open(source_path) as im:
            im.verify()
        with Image.open(source_path) as im:
            width, height = im.size
    except Exception as exc:
        fail("Cannot decode reference image: " + str(exc))
    if width < 256 or height < 256:
        fail("Reference image is too small; choose a clearer image of at least 256x256.")
    relative_source = PurePosixPath(raw_source).as_posix()
    source_url = "https://raw.githubusercontent.com/" + repo + "/" + commit_sha + "/" + quote(relative_source, safe="/")
    embedded_prompt, metadata_keys = extract_embedded_prompt(source_path, root)
    out_dir = root / "generated" / "hairstyles" / character_id / ("run-" + str(run_id))
    out_dir.mkdir(parents=True, exist_ok=True)
    crop_path = out_dir / "reference-head-crop.png"
    head_data_url, crop_metadata = prepare_head_reference(source_path, crop_path, head_crop_height_ratio)
    crop_sha = hashlib.sha256(crop_path.read_bytes()).hexdigest()
    if generation_mode == "preview":
        preview = {
            "mode": "preview_only_no_paid_generation",
            "character_id": character_id,
            "source_path": relative_source,
            "source_sha256": source_sha,
            "source_dimensions": [width, height],
            "head_crop_path": str(crop_path.relative_to(root)),
            "head_crop_sha256": crop_sha,
            "head_crop": crop_metadata,
            "message": "Review reference-head-crop.png before running with GENERATION_MODE=generate.",
        }
        (out_dir / "reference-preview.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Preview only: created the crop and provenance manifest. No external AI API was called.")
        return
    visual_analysis = infer_visual_base_prompt(head_data_url, requests)
    visual_base_prompt = visual_analysis["visual_base_prompt"]
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    created, manifest_variants = [], []
    prompt_sections = [
        "# Hairstyle generation prompts — " + character_id, "",
        "- Source: " + relative_source,
        "- Source SHA-256: " + source_sha,
        "- Source dimensions: " + str(width) + "x" + str(height),
        "- API reference: cropped head-only canvas; full original body is not sent",
        "- Head crop box (pixels): " + str(crop_metadata["crop_box_pixels"]),
        "- Cropped reference SHA-256: " + crop_sha,
        "- Model: " + MODEL, "- Run: " + str(run_id), "",
        "The exact prompts used by this run are listed below. The source prompt is recorded only when present in image metadata; it is never guessed.", "",
    ]
    if embedded_prompt:
        prompt_sections += ["## Prompt recovered from embedded source metadata", "", "~~~text", embedded_prompt, "~~~", ""]
    else:
        prompt_sections += ["## Source metadata", "", "No recognized embedded source prompt was found. No original prompt is claimed.", ""]
    prompt_sections += ["## Candidate stable-character prompt inferred from the cropped image", "", "This is a visual reconstruction, not the original image-generation prompt; it needs human review.", "", "~~~text", visual_base_prompt, "~~~", ""]
    variants = STYLE_PACKS[style_pack]
    for index, (slug, hair_description) in enumerate(variants, start=1):
        prompt = BASE_INSTRUCTIONS + " Stable character identity prompt, inferred from the reference and excluding the hairstyle: " + visual_base_prompt + ". Specific hairstyle for this version: " + hair_description + ". Return one polished image."
        payload = {
            "model": MODEL, "images": [{"image_url": head_data_url}], "prompt": prompt,
            "size": "1024x1024", "quality": "medium", "output_format": "webp", "n": 1,
        }
        print("[" + str(index) + "/" + str(len(variants)) + "] Generating " + slug + "...", flush=True)
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=(30, 900))
        except requests.RequestException as exc:
            fail("Request failed for " + slug + ": " + str(exc))
        if not response.ok:
            fail("Image API returned HTTP " + str(response.status_code) + " for " + slug + ": " + response.text[:1800])
        try:
            item = response.json()["data"][0]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            fail("Unexpected API response for " + slug + ": " + str(exc))
        target = out_dir / (str(index).zfill(2) + "-" + slug + ".webp")
        if item.get("b64_json"):
            target.write_bytes(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            try:
                img_response = requests.get(item["url"], timeout=(20, 180))
                img_response.raise_for_status()
                target.write_bytes(img_response.content)
            except requests.RequestException as exc:
                fail("Could not retrieve generated file for " + slug + ": " + str(exc))
        else:
            fail("No image bytes or URL were returned for " + slug + ".")
        try:
            with Image.open(target) as check:
                check.verify()
        except Exception as exc:
            fail("Generated output is not a valid image (" + target.name + "): " + str(exc))
        created.append((slug, target))
        manifest_variants.append({
            "index": index, "hairstyle_id": slug, "hairstyle_description": hair_description,
            "file": target.name, "prompt": prompt,
        })
        prompt_sections += ["## " + str(index) + ". " + slug, "", "Style: " + hair_description, "", "~~~text", prompt, "~~~", ""]
    render_contact_sheet(created, out_dir / "contact-sheet.jpg")
    manifest = {
        "schema_version": 1, "character_id": character_id, "style_pack": style_pack,
        "model": MODEL, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": repo, "commit": commit_sha, "path": relative_source,
            "raw_url": source_url, "sha256": source_sha, "width": width, "height": height,
            "head_crop_path": str(crop_path.relative_to(root)), "head_crop_sha256": crop_sha,
            "head_crop": crop_metadata,
            "visual_analysis": visual_analysis,
            "api_input_note": "Only reference-head-crop.png is sent to the image edit API and vision analysis; the full original image is not sent.",
            "metadata_keys": metadata_keys, "embedded_prompt_found": bool(embedded_prompt),
            "embedded_prompt": embedded_prompt or None,
        },
        "variants": manifest_variants,
        "review_note": "Human review required: image editing can change details outside the hair. Keep only variants that preserve the character identity.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "PROMPTS.md").write_text("\n".join(prompt_sections), encoding="utf-8")

    # Keep a verifiable per-character source-prompt history without guessing a canonical prompt.
    registry_path = root / "data" / "character-prompt-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        character = next(item for item in registry["characters"] if item["id"] == character_id)
    except Exception as exc:
        fail("Could not safely update the character prompt registry: " + str(exc))
    if relative_source not in character.setdefault("source_images", []):
        character["source_images"].append(relative_source)
    examples = character.setdefault("source_prompt_examples", [])
    if not any(item.get("source_sha256") == source_sha for item in examples):
        examples.append({
            "source_path": relative_source,
            "source_sha256": source_sha,
            "source_prompt": embedded_prompt or None,
            "prompt_status": "recovered_from_embedded_metadata" if embedded_prompt else "not_found_in_embedded_metadata",
            "visual_base_prompt": visual_base_prompt,
            "visual_prompt_model": visual_analysis["model"],
            "visual_prompt_status": "inferred_from_cropped_image_not_original_prompt",
            "stable_traits": visual_analysis["stable_traits"],
            "uncertainties": visual_analysis["uncertainties"],
            "run_id": str(run_id),
            "head_crop_path": str(crop_path.relative_to(root)),
            "review_status": "needs_manual_review",
        })
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(created)} hairstyle images, prompt records, manifest, contact sheet and updated character source-prompt history in {out_dir.relative_to(root)}")

if __name__ == "__main__":
    main()
