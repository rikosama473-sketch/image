#!/usr/bin/env python3
"""Create identity-preserving visual variants from a real IMAGE repository reference."""
from __future__ import annotations
import argparse, hashlib, io, json, re, sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

SPACE_ID = "conradlocke/krea2-identity-edit"
SPACE_URL = "https://huggingface.co/spaces/conradlocke/krea2-identity-edit"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_SOURCE_BYTES = 20 * 1024 * 1024

BASE = (
    "Precise image-to-image edit of the supplied original anime character illustration, not a new character. "
    "Preserve exact recognizable identity, face shape, eye shape and color except when this named variant explicitly edits the eyes, "
    "skin tone, hair color except when explicitly requested, existing accessories except when adding one, body proportions, line art, "
    "shading, palette, clothing, pose, framing and background. Make only the single change requested below. Keep every other region "
    "as close to the source as possible. Do not add text, logos, watermarks, characters, clothing or props that were not requested. "
    "Do not turn the anime illustration photorealistic."
)
PACKS = {
    "hair-core-5": [
        ("blunt-bob", "Change only the hairstyle to a neat blunt bob ending at the chin, smooth rounded silhouette, clear blunt ends. Keep the original hair color."),
        ("long-straight", "Change only the hairstyle to long straight hair falling below the shoulders, smooth strands and a clean silhouette. Keep the original hair color."),
        ("high-ponytail", "Change only the hairstyle to a high ponytail tied at the crown, flowing length and restrained framing strands. Keep the original hair color."),
        ("twin-tails", "Change only the hairstyle to balanced twin tails tied on both sides, matching volume and length. Keep the original hair color."),
        ("side-braid", "Change only the hairstyle to one substantial side braid resting over one shoulder, with clearly visible woven strands. Keep the original hair color."),
    ],
    "expressions-core-5": [
        ("happy", "Change only the facial expression to a warm, readable smile with gently lifted cheeks. Keep eyes, hairstyle, accessories, clothes and pose unchanged."),
        ("surprised", "Change only the expression to mild surprise: raised brows, more open eyes and a small parted mouth. Keep hairstyle, eye color, accessories, clothes and pose unchanged."),
        ("sad", "Change only the expression to quiet sadness with softly lowered brows and a slightly downturned mouth. Keep hairstyle, eye color, accessories, clothes and pose unchanged."),
        ("annoyed", "Change only the expression to restrained annoyance with subtly narrowed eyes, lowered brows and a small frown. Keep hairstyle, eye color, accessories, clothes and pose unchanged."),
        ("shy", "Change only the expression to shy embarrassment with a restrained cheek blush and hesitant smile. Keep hairstyle, eye color, accessories, clothes and pose unchanged."),
    ],
    "eyes-4": [
        ("eye-catchlights", "Keep original iris color and expression. Add a soft secondary catchlight to each iris only; change nothing else."),
        ("eye-iris-rings", "Keep original iris color and expression. Make iris rings slightly more defined and pupils crisp; preserve original eye shape and all other details."),
        ("eye-upper-highlight", "Keep original iris color and expression. Add a subtle anime-style upper iris highlight while keeping the original eye shape, eyelashes and eyebrows."),
        ("eye-lower-lash", "Keep original iris color and expression. Add a tidy, subtle lower-lash detail only; do not change eye shape or other features."),
    ],
    "accessories-4": [
        ("ribbon", "Add one small tasteful ribbon hair accessory suited to the existing palette. Preserve all existing accessories; change nothing else."),
        ("hair-clip", "Add one small simple hair clip near the temple, coordinated with the existing palette. Preserve existing accessories; change nothing else."),
        ("star-pin", "Add one tiny star-shaped hair pin near the temple. Preserve existing accessories; change nothing else."),
        ("headband", "Add one slim, simple headband that fits the existing palette without covering the eyes. Preserve existing accessories; change nothing else."),
    ],
    "face-details-4": [
        ("freckles", "Add a very light cluster of tiny freckles across the upper cheeks only. Do not alter face shape, skin tone, expression, eye color, hairstyle or accessories."),
        ("beauty-mark", "Add one tiny, subtle beauty mark beneath one eye. Do not alter face structure, skin tone, expression, eye color, hairstyle or accessories."),
        ("soft-blush", "Add a soft restrained cheek blush that matches the source palette. Do not alter face shape, skin tone, expression, eye color, hairstyle or accessories."),
        ("lower-eyeliner", "Add a fine, subtle anime-style lower eyeliner detail while preserving exact eye shape, iris color and expression."),
    ],
}

def fail(message):
    print("ERROR: " + str(message), file=sys.stderr)
    raise SystemExit(1)

def validate_path(raw):
    raw = raw.strip()
    p = PurePosixPath(raw)
    if not raw or p.is_absolute() or ".." in p.parts or "\\" in raw or p.suffix.lower() not in ALLOWED_EXTENSIONS:
        fail("Reference must be a safe repository-relative PNG, JPG/JPEG or WebP path.")
    return p.as_posix()

def source_url(repo, ref, path):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        fail("Invalid repository name.")
    if not ref or "\n" in ref or "\r" in ref:
        fail("Invalid source revision.")
    return f"https://raw.githubusercontent.com/{repo}/{quote(ref, safe='/')}/{quote(path, safe='/')}"

def load_source(url, dest):
    try:
        response = requests.get(url, timeout=(20, 120))
        response.raise_for_status()
    except requests.RequestException as exc:
        fail("Source image download failed: " + str(exc))
    raw = response.content
    if not raw or len(raw) > MAX_SOURCE_BYTES:
        fail("Source image is empty or larger than 20 MiB.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    try:
        with Image.open(dest) as im:
            im.verify()
        with Image.open(dest) as im:
            im = ImageOps.exif_transpose(im)
            dims = im.size
    except Exception as exc:
        fail("Invalid source raster image: " + str(exc))
    if min(dims) < 256:
        fail("Source image must be at least 256x256 pixels.")
    return hashlib.sha256(raw).hexdigest(), dims

def normalize_output(value, dest):
    used_seed = None
    if isinstance(value, (tuple, list)):
        if not value:
            fail("The image editor returned no output.")
        if len(value) > 1:
            try: used_seed = int(value[1])
            except (ValueError, TypeError): pass
        value = value[0]
    if isinstance(value, Image.Image):
        image = value.copy()
    elif isinstance(value, dict):
        path, url = value.get("path"), value.get("url")
        if path and Path(str(path)).is_file():
            image = Image.open(str(path)).copy()
        elif url:
            image = fetch_image(str(url))
        else:
            fail("Returned image object has no readable file or URL.")
    elif isinstance(value, str) and Path(value).is_file():
        image = Image.open(value).copy()
    elif isinstance(value, str) and value.startswith(("https://", "http://")):
        image = fetch_image(value)
    else:
        fail("Could not read the output image returned by the public Space.")
    image = ImageOps.exif_transpose(image)
    if min(image.size) < 256:
        fail("Generated image is smaller than 256x256.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, format="PNG", optimize=True)
    with Image.open(dest) as check: check.verify()
    return hashlib.sha256(dest.read_bytes()).hexdigest(), used_seed, image.size

def fetch_image(url):
    try:
        response = requests.get(url, timeout=(20, 180))
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).copy()
    except Exception as exc:
        fail("Could not download generated image: " + str(exc))

def make_cutout(flat_path, cutout_path, session):
    from rembg import remove
    raw = remove(flat_path.read_bytes(), session=session)
    with Image.open(io.BytesIO(raw)) as im:
        rgba = im.convert("RGBA")
    cutout_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(cutout_path, format="PNG", optimize=True)
    hist = rgba.getchannel("A").histogram()
    total = max(1, rgba.width * rgba.height)
    transparent = hist[0] / total
    opaque = hist[255] / total
    warning = None
    if opaque < .05: warning = "Very little fully opaque foreground; inspect the cutout."
    elif transparent < .01: warning = "Very little transparency was created; inspect background edges."
    return {
        "file": cutout_path.as_posix(),
        "sha256": hashlib.sha256(cutout_path.read_bytes()).hexdigest(),
        "dimensions": list(rgba.size),
        "transparent_pixel_ratio": round(transparent, 5),
        "opaque_pixel_ratio": round(opaque, 5),
        "quality_warning": warning,
    }

def make_contact_sheet(items, target):
    cols, cell_w, cell_h, label_h, margin = 3, 360, 420, 40, 16
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*cell_w + (cols+1)*margin, rows*(cell_h+label_h) + (rows+1)*margin), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError: font = ImageFont.load_default()
    for i, (label, path) in enumerate(items):
        with Image.open(path) as im:
            im = im.convert("RGBA")
            im.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        row, col = divmod(i, cols)
        x, y = margin + col*(cell_w+margin), margin + row*(cell_h+label_h+margin)
        board = Image.new("RGBA", (cell_w, cell_h), "#ffffff")
        checker = Image.new("RGBA", (24,24), "#e2e2e2")
        cd = ImageDraw.Draw(checker); cd.rectangle((0,0,11,11), fill="#bdbdbd"); cd.rectangle((12,12,23,23), fill="#bdbdbd")
        for yy in range(0, cell_h, 24):
            for xx in range(0, cell_w, 24): board.alpha_composite(checker, (xx,yy))
        board.alpha_composite(im, ((cell_w-im.width)//2, (cell_h-im.height)//2))
        sheet.paste(board.convert("RGB"), (x,y))
        draw.rectangle((x,y+cell_h,x+cell_w,y+cell_h+label_h), fill="#ffffff")
        draw.text((x+10,y+cell_h+10), label.replace("-", " "), fill="#202020", font=font)
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="JPEG", quality=88, optimize=True)

def update_registry(path, cid, source, sha, run_record):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        char = next(x for x in data["characters"] if x["id"] == cid)
    except Exception as exc:
        fail("Could not update character registry safely: " + str(exc))
    if source not in char.setdefault("source_images", []): char["source_images"].append(source)
    runs = char.setdefault("asset_runs", [])
    if not any(x.get("run_id") == run_record["run_id"] for x in runs): runs.append(run_record)
    char["asset_generation_status"] = "generated_pending_visual_review"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repository", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--character", required=True, choices=["pibara", "sunna", "chie"])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--pack", required=True, choices=sorted(PACKS))
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--seed", type=int, default=1201)
    ap.add_argument("--keep-background", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    path = validate_path(args.reference)
    url = source_url(args.repository, args.ref, path)
    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    run_id = re.sub(r"[^A-Za-z0-9_.-]", "-", str(args.run_id))
    out = root / "generated" / "character-assets" / args.character / day / ("run-" + run_id)
    cache = root / ".cache" / "character-assets" / (Path(path).name)
    source_sha, source_dims = load_source(url, cache)
    renders, cutouts = out / "renders", out / "transparent"
    renders.mkdir(parents=True, exist_ok=True)

    try:
        from gradio_client import Client, handle_file
        client = Client(SPACE_ID, verbose=True)
        # Krea2's public ImageData schema supports an image supplied by URL; no file upload or token is needed.
        source_input = handle_file(url)
    except Exception as exc:
        fail("Could not connect to the public Gradio Space: " + str(exc))

    cutout_session = None
    if not args.keep_background:
        try:
            from rembg import new_session
            cutout_session = new_session("u2net")
        except Exception as exc:
            print("WARNING: transparent cutouts unavailable: " + str(exc), file=sys.stderr)

    variants, contact_items, prompt_sections = [], [], []
    for i, (slug, change) in enumerate(PACKS[args.pack], start=1):
        prompt = BASE + " Requested single change: " + change
        seed = max(0, min(2147483647, args.seed + i - 1))
        flat = renders / f"{i:02d}-{slug}.png"
        print(f"[{i}/{len(PACKS[args.pack])}] Generating {args.character}/{slug}", flush=True)
        try:
            result = client.predict(
                source_image=source_input,
                instruction=prompt,
                ref_boost=4.0,
                grounding_px=768,
                lora_scale=1.0,
                steps=12,
                guidance_scale=0.0,
                seed=seed,
                randomize_seed=False,
                api_name="/edit",
            )
        except Exception as exc:
            fail("Public image edit failed for " + slug + ": " + str(exc))
        flat_sha, returned_seed, dims = normalize_output(result, flat)
        rec = {
            "index": i, "asset_id": slug, "change": change, "prompt": prompt,
            "requested_seed": seed, "returned_seed": returned_seed,
            "render": {"file": flat.relative_to(root).as_posix(), "sha256": flat_sha, "dimensions": list(dims)},
            "transparent_layer": None,
        }
        contact_path = flat
        if cutout_session is not None:
            cutout = cutouts / f"{i:02d}-{slug}.png"
            try:
                cut = make_cutout(flat, cutout, cutout_session)
                cut["file"] = cutout.relative_to(root).as_posix()
                rec["transparent_layer"] = cut
                contact_path = cutout
            except Exception as exc:
                rec["transparent_layer"] = {"error": str(exc), "status": "not_created"}
                print("WARNING: cutout failed for " + slug + ": " + str(exc), file=sys.stderr)
        contact_items.append((slug, contact_path))
        variants.append(rec)
        prompt_sections.append(f"## {slug}\n\nRequested seed: {seed}\n\n~~~text\n{prompt}\n~~~")

    contact_path = out / "contact-sheet.jpg"
    make_contact_sheet(contact_items, contact_path)
    manifest = {
        "schema_version": 1, "character_id": args.character, "pack": args.pack,
        "created_at_utc": now.isoformat(),
        "source": {"repository": args.repository, "ref": args.ref, "path": path, "url": url, "sha256": source_sha, "dimensions": list(source_dims)},
        "generator": {
            "space_id": SPACE_ID, "space_url": SPACE_URL, "api_name": "/edit",
            "openai_api_key_used": False, "inference_api_paid_by_openai": False,
            "ref_boost": 4.0, "grounding_px": 768, "lora_scale": 1.0, "steps": 12,
            "guidance_scale": 0.0, "background_removed": cutout_session is not None,
        },
        "variants": variants,
        "review_status": "needs_visual_identity_review",
        "warning": "Generated renders and automatic cutouts require visual review of character likeness and hair/accessory edges.",
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prompts_text = "# Generated prompts\n\nCharacter: " + args.character + "\n\nSource: " + path + "\n\nSource SHA-256: " + source_sha + "\n\nGenerator: " + SPACE_URL + "\n\n" + "\n\n".join(prompt_sections) + "\n"
    (out / "PROMPTS.md").write_text(prompts_text, encoding="utf-8")
    record = {
        "run_id": run_id, "date": day, "pack": args.pack, "source_path": path,
        "source_sha256": source_sha, "manifest_path": (out/"manifest.json").relative_to(root).as_posix(),
        "contact_sheet_path": contact_path.relative_to(root).as_posix(),
        "variant_count": len(variants), "review_status": "needs_visual_identity_review",
    }
    update_registry(root / "data" / "character-prompt-registry.json", args.character, path, source_sha, record)
    print(f"SUCCESS: created {len(variants)} variants under {out.relative_to(root)}")
    print("The original reference was not modified.")

if __name__ == "__main__":
    main()
