#!/usr/bin/env python3
"""Download and safely unpack the project's two reviewed CC0 art packages.

Only downloads assets from the allow-listed original OpenGameArt URLs below.
Packages go to data/asset-cache (git-ignored) and are never treated as approved
training data automatically. No original repository images are changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "asset-cache"
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_EXTRACTED_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 500
USER_AGENT = "IMAGE-asset-acquisition/1.0 (+https://github.com/rikosama473-sketch/image)"

PACKS: dict[str, dict[str, Any]] = {
    "anime-portraits": {
        "title": "Anime Girl and Boy Portraits — stevenburrow",
        "url": "https://opengameart.org/sites/default/files/allanime-11-28-2020.zip",
        "source_page": "https://opengameart.org/content/anime-girl-and-boy-portraits",
        "license": "CC0 as declared on the original OpenGameArt source page",
        "archive_name": "allanime-11-28-2020.zip",
        "expected_bytes": 3517503,
        "purpose": "Anime-style editable face, eye, mouth and hair components; not a full-body kit.",
    },
    "modular-64x96": {
        "title": "Customizable Character Pack — rubberduck",
        "url": "https://opengameart.org/sites/default/files/customizable_characters_w_samples.zip",
        "source_page": "https://opengameart.org/content/customizable-character-pack",
        "license": "CC0 as declared on the original OpenGameArt source page",
        "archive_name": "customizable_characters_w_samples.zip",
        "expected_bytes": 252884,
        "purpose": "Modular GIMP source and 16 sample characters at 64x96; pixel/cartoon style, useful for alignment tests.",
    },
    "visual-novel-characters": {
        "title": "Visual Novel Style Characters — madameberry",
        "url": "https://opengameart.org/sites/default/files/VisualNovel_Set1_MadameBerry.zip",
        "source_page": "https://opengameart.org/node/54368",
        "license": "CC0 as declared on the original OpenGameArt source page",
        "archive_name": "VisualNovel_Set1_MadameBerry.zip",
        "expected_bytes": None,
        "purpose": "Visual-novel-style characters with layered PSD and exported PNG files; review each layer before mixing.",
    }
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validated_members(archive: zipfile.ZipFile) -> list[tuple[zipfile.ZipInfo, PurePosixPath]]:
    infos = archive.infolist()
    if len(infos) > MAX_ARCHIVE_MEMBERS:
        raise ValueError(f"Archive has too many entries ({len(infos)} > {MAX_ARCHIVE_MEMBERS}).")

    checked: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
    total = 0
    seen: set[str] = set()
    for info in infos:
        name = info.filename.replace("\\", "/")
        member = PurePosixPath(name)
        if not name or member.is_absolute() or any(part in ("", ".", "..") for part in member.parts):
            raise ValueError(f"Unsafe archive path: {info.filename!r}")
        if member.parts and ":" in member.parts[0]:
            raise ValueError(f"Drive-like archive path is not allowed: {info.filename!r}")
        mode = (info.external_attr >> 16) & 0o170000
        if stat.S_ISLNK(mode):
            raise ValueError(f"Symbolic links are not allowed in archives: {info.filename!r}")
        key = member.as_posix().casefold()
        if key in seen:
            raise ValueError(f"Duplicate archive path: {info.filename!r}")
        seen.add(key)
        total += info.file_size
        if total > MAX_EXTRACTED_BYTES:
            raise ValueError(f"Archive expands beyond {MAX_EXTRACTED_BYTES} bytes.")
        if info.file_size < 0:
            raise ValueError(f"Invalid file size for {info.filename!r}")
        checked.append((info, member))
    return checked


def safe_extract_zip(archive_path: Path, destination: Path) -> list[str]:
    """Extract regular ZIP members after validating all paths and size limits."""
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    with zipfile.ZipFile(archive_path) as archive:
        members = _validated_members(archive)
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC check failed for {bad!r}")
        root = destination.resolve()
        for info, member in members:
            target = (destination / Path(*member.parts)).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"Archive entry escapes destination: {info.filename!r}")
        for info, member in members:
            target = destination / Path(*member.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            extracted.append(member.as_posix())
    return sorted(extracted)


def unique_backup_path(path: Path) -> Path:
    candidate = path.with_name(path.name + ".previous")
    index = 1
    while candidate.exists():
        candidate = path.with_name(path.name + f".previous-{index}")
        index += 1
    return candidate


def download_pack(pack_id: str, output_root: Path, force: bool = False) -> dict[str, Any]:
    pack = PACKS[pack_id]
    download_dir = output_root / "downloads"
    extract_root = output_root / "extracted"
    download_dir.mkdir(parents=True, exist_ok=True)
    extract_root.mkdir(parents=True, exist_ok=True)
    archive_path = download_dir / pack["archive_name"]
    extract_path = extract_root / pack_id

    if archive_path.exists():
        if not force:
            if pack.get("expected_bytes") is not None and archive_path.stat().st_size != pack["expected_bytes"]:
                raise ValueError(
                    f"{archive_path} exists but size differs from the reviewed archive. "
                    "Inspect it manually or rerun with --force."
                )
        else:
            archive_path.replace(unique_backup_path(archive_path))

    if not archive_path.exists():
        temp_path = archive_path.with_name(archive_path.name + ".part")
        if temp_path.exists():
            temp_path.replace(unique_backup_path(temp_path))
        request = urllib.request.Request(pack["url"], headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=45) as response, temp_path.open("xb") as output:
                final_url = response.geturl()
                if not final_url.startswith("https://"):
                    raise ValueError("Refusing a non-HTTPS download destination.")
                downloaded = 0
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    downloaded += len(block)
                    if downloaded > MAX_ARCHIVE_BYTES:
                        raise ValueError(f"Download exceeded {MAX_ARCHIVE_BYTES} bytes.")
                    output.write(block)
            if pack.get("expected_bytes") is not None and downloaded != pack["expected_bytes"]:
                raise ValueError(
                    f"Downloaded {downloaded} bytes, expected {pack['expected_bytes']}. "
                    "The publisher may have changed the archive; do not extract until reviewed."
                )
            if not zipfile.is_zipfile(temp_path):
                raise ValueError("The downloaded file is not a ZIP archive.")
            temp_path.replace(archive_path)
        except Exception:
            if temp_path.exists():
                temp_path.replace(unique_backup_path(temp_path))
            raise

    if not zipfile.is_zipfile(archive_path):
        raise ValueError(f"{archive_path} is not a valid ZIP archive.")
    if pack.get("expected_bytes") is not None and archive_path.stat().st_size != pack["expected_bytes"]:
        raise ValueError("Archive size differs from the recorded source snapshot.")

    if extract_path.exists():
        if not force:
            return {
                **pack,
                "id": pack_id,
                "archive_path": archive_path.relative_to(output_root).as_posix(),
                "archive_bytes": archive_path.stat().st_size,
                "sha256": sha256_file(archive_path),
                "extract_path": extract_path.relative_to(output_root).as_posix(),
                "status": "already-extracted-no-files-overwritten",
            }
        extract_path.replace(unique_backup_path(extract_path))

    staging = Path(tempfile.mkdtemp(prefix=f".{pack_id}-extract-", dir=extract_root))
    try:
        file_tree = safe_extract_zip(archive_path, staging)
        staging.replace(extract_path)
    except Exception:
        if staging.exists():
            staging.replace(unique_backup_path(staging))
        raise

    return {
        **pack,
        "id": pack_id,
        "archive_path": archive_path.relative_to(output_root).as_posix(),
        "archive_bytes": archive_path.stat().st_size,
        "sha256": sha256_file(archive_path),
        "extract_path": extract_path.relative_to(output_root).as_posix(),
        "file_tree": file_tree,
        "status": "downloaded-and-extracted-unreviewed",
        "license_note": "Source page license is recorded; still review terms before redistribution or training. Downloading does not approve assets.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", choices=sorted([*PACKS, "all"]), default="all")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Refresh downloaded/extracted files while preserving prior copies as .previous backups.")
    args = parser.parse_args()

    output_root = args.output_root.expanduser().resolve()
    selected = list(PACKS) if args.pack == "all" else [args.pack]
    manifest_path = output_root / "acquisition-manifest.json"
    previous: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise SystemExit(f"Cannot read existing manifest: {manifest_path}")

    results = []
    for pack_id in selected:
        result = download_pack(pack_id, output_root, force=args.force)
        previous.setdefault("schemaVersion", 1)
        previous.setdefault("project", "IMAGE")
        previous.setdefault("items", {})
        previous["items"][pack_id] = result
        results.append(result)

    previous["updatedAt"] = "local-run; see file metadata for exact timestamp"
    manifest_path.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Acquisition manifest: {manifest_path}")
    for item in results:
        print(f"- {item['id']}: {item['status']} | {item['archive_bytes']} bytes | sha256={item['sha256']}")
        print(f"  extracted: {output_root / item['extract_path']}")
    print("Downloaded graphics remain outside Git's tracked assets until each file and its intended usage are reviewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
