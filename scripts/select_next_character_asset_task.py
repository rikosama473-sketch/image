#!/usr/bin/env python3
"""Select the next incomplete character asset pack for the daily no-key worker."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CHARACTER_ORDER = ("pibara", "sunna", "chie")
PACK_ORDER = ("hair-core-5", "expressions-core-5", "eyes-4", "accessories-4", "face-details-4")
CONFIRMED_PIBARA_REFERENCE = "from-PixAI-2034984086876227343-0.png"


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _pack_completed(root: Path, character_id: str, reference: str, source_sha: str, pack: str) -> bool:
    base = root / "generated" / "character-assets" / character_id
    if not base.is_dir():
        return False
    for manifest_path in base.rglob("manifest.json"):
        manifest = _load_json(manifest_path)
        if not manifest:
            continue
        source = manifest.get("source") or {}
        if (
            manifest.get("character_id") != character_id
            or manifest.get("pack") != pack
            or source.get("path") != reference
            or source.get("sha256") != source_sha
            or manifest.get("pack_status") != "complete"
        ):
            continue
        required = set(manifest.get("required_asset_ids") or [])
        completed = set(manifest.get("completed_asset_ids") or [])
        variants = manifest.get("variants") or []
        if not required or not required.issubset(completed):
            continue
        render_ids = {
            record.get("asset_id")
            for record in variants
            if isinstance(record, dict)
            and record.get("render")
            and (root / str(record["render"].get("file", ""))).is_file()
        }
        if required.issubset(render_ids):
            return True
    return False


def select_next_task(root: Path) -> dict[str, str] | None:
    registry_path = root / "data" / "character-prompt-registry.json"
    registry = _load_json(registry_path)
    if not registry:
        return None
    characters = registry.get("characters") or []
    by_id = {item.get("id"): item for item in characters if isinstance(item, dict)}
    for character_id in CHARACTER_ORDER:
        character = by_id.get(character_id)
        if not character:
            continue
        references = character.get("source_images") or []
        if isinstance(references, str):
            references = [references]
        for reference in references:
            if not isinstance(reference, str) or not reference.strip():
                continue
            reference = reference.strip()
            # Avoid the one known cross-character mistake: Pibara's reference
            # must never be silently reused for Chie or Sunna.
            if character_id != "pibara" and reference == CONFIRMED_PIBARA_REFERENCE:
                continue
            source_path = root / reference
            if not source_path.is_file():
                continue
            try:
                sha = source_sha256(source_path)
            except OSError:
                continue
            for pack in PACK_ORDER:
                if not _pack_completed(root, character_id, reference, sha, pack):
                    return {
                        "run": "true",
                        "character_id": character_id,
                        "reference_image": reference,
                        "asset_pack": pack,
                        "reason": f"first incomplete pack for {character_id} from {reference}",
                    }
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    task = select_next_task(root)
    if task is None:
        registry = _load_json(root / "data" / "character-prompt-registry.json") or {}
        characters = {item.get("id"): item for item in registry.get("characters", []) if isinstance(item, dict)}
        missing = [name for name in ("sunna", "chie") if not (characters.get(name, {}).get("source_images") or [])]
        message = "No queued task has a verified, existing reference."
        if missing:
            message += " Missing confirmed source image(s) for: " + ", ".join(missing) + "."
        print("run=false")
        print("reason=" + message)
        print(message, file=sys.stderr)
        return 0
    for key in ("run", "character_id", "reference_image", "asset_pack", "reason"):
        print(f"{key}={task[key]}")
    print(f"Scheduled next: {task['character_id']} / {task['asset_pack']} / {task['reference_image']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
