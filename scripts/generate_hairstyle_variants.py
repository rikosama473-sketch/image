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
    "Create a hairstyle-study edit based on the supplied cropped head reference; preserve the same character identity. "
    "Change ONLY the hairstyle and arrangement of the hair. Preserve the face, eye shape and color, glasses, expression, "
    "adult appearance, skin tone, head proportions, hair color, accessories unless physically incompatible, line art, "
    "shading, palette and rendering style. Do not redesign the face or add characters, text, logos or watermarks. "
    "Present a centered head-and-hair portrait against a clean neutral background, with a simple fully covering high-neck "
    "top visible only at the bottom if shoulders appear. No nudity, cleavage or torso detail. Make the hairstyle silhouette, "
    "parting, strand direction, volume and ends the dominant variable. Preserve everything outside the hair as closely as possible."
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

def extract_embedded_prompt(image_path):
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

def prepare_head_reference(source_path, target_path):
    """Crop the upper head zone and place it on a neutral canvas before calling the image API.

    The full source image is never sent to the image-edit endpoint. The crop is designed for
    upright anime illustrations whose head begins near the top edge; inspect the saved crop.
    """
    with Image.open(source_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    width, height = image.size
    left = int(round(width * 0.02))
    right = int(round(width * 0.98))
    bottom = max(256, min(int(round(width * 0.40)), int(round(height * 0.28))))
    bottom = min(height, bottom)
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
        "crop_method": "top head zone based on width/height; original pixels outside the crop are excluded",
    }


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
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        fail("Missing Actions secret OPENAI_API_KEY. Never put the API key in source code.")
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    commit_sha = os.environ.get("GITHUB_SHA", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    character_id = os.environ.get("CHARACTER_ID", "").strip().lower()
    style_pack = os.environ.get("STYLE_PACK", "core-6").strip().lower()
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
    embedded_prompt, metadata_keys = extract_embedded_prompt(source_path)
    out_dir = root / "generated" / "hairstyles" / character_id / ("run-" + str(run_id))
    out_dir.mkdir(parents=True, exist_ok=True)
    crop_path = out_dir / "reference-head-crop.png"
    head_data_url, crop_metadata = prepare_head_reference(source_path, crop_path)
    crop_sha = hashlib.sha256(crop_path.read_bytes()).hexdigest()
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
        prompt_sections += ["## Source metadata", "", "No recognized embedded source prompt was found. No source prompt has been invented.", ""]
    variants = STYLE_PACKS[style_pack]
    for index, (slug, hair_description) in enumerate(variants, start=1):
        prompt = BASE_INSTRUCTIONS + " Specific hairstyle for this version: " + hair_description + ". Return one polished image."
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
            "api_input_note": "Only reference-head-crop.png is sent to the image edit API; the full original image is not sent.",
            "metadata_keys": metadata_keys, "embedded_prompt_found": bool(embedded_prompt),
            "embedded_prompt": embedded_prompt or None,
        },
        "variants": manifest_variants,
        "review_note": "Human review required: image editing can change details outside the hair. Keep only variants that preserve the character identity.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "PROMPTS.md").write_text("\n".join(prompt_sections), encoding="utf-8")
    print("Created six images, prompt records, manifest and contact sheet in " + str(out_dir.relative_to(root)))

if __name__ == "__main__":
    main()
