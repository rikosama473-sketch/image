#!/usr/bin/env python3
"""Publish a reviewed asset folder to an existing non-default GitHub branch."""
from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path, PurePosixPath
import re

ALLOWED_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg", ".json", ".md"}
MAX_FILE_BYTES = 90 * 1024 * 1024
MAX_TOTAL_BYTES = 95 * 1024 * 1024


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-_").lower()
    if not slug or slug in {".", ".."}:
        raise ValueError("Character ID must contain letters/numbers and optional '-' or '_'.")
    return slug


def safe_target_prefix(value: str, character_id: str) -> str:
    normalized = value.format(character_id=safe_slug(character_id)).strip("/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("Target prefix must be a safe repository-relative path.")
    if "\\" in normalized or "\n" in normalized or "\r" in normalized:
        raise ValueError("Target prefix contains unsupported characters.")
    return path.as_posix()


def collect_publish_files(root: Path) -> list[tuple[Path, str]]:
    if root.is_symlink():
        raise ValueError("Asset directory itself must not be a symlink.")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Asset directory must be a directory: {root}")
    files: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not publishable: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Unsupported filesystem entry: {path}")
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"Unsupported asset file type: {path.suffix or '[no extension]'}")
        relative = path.relative_to(root).as_posix()
        rel_path = PurePosixPath(relative)
        if rel_path.is_absolute() or any(part in {"", ".", ".."} for part in rel_path.parts):
            raise ValueError(f"Unsafe asset path: {relative}")
        size = path.stat().st_size
        if size <= 0 or size > MAX_FILE_BYTES:
            raise ValueError(f"File size must be 1 byte to {MAX_FILE_BYTES} bytes: {relative}")
        files.append((path, relative))
    if not files:
        raise ValueError("No publishable assets found.")
    total = sum(path.stat().st_size for path, _ in files)
    if total > MAX_TOTAL_BYTES:
        raise ValueError(f"Asset set exceeds total limit of {MAX_TOTAL_BYTES} bytes.")
    return files


def publish(repo_name: str, branch_name: str, asset_dir: Path, character_id: str, message: str) -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise ValueError("Set GITHUB_TOKEN or GH_TOKEN in the local environment; never pass tokens as CLI arguments.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_name):
        raise ValueError("Repository must be OWNER/NAME.")
    char_id = safe_slug(character_id)

    try:
        from github import Auth, Github, InputGitTreeElement
    except ImportError as exc:
        raise RuntimeError("Install optional upload dependencies with: python -m pip install -r requirements-publish.txt") from exc

    github = Github(auth=Auth.Token(token), timeout=30)
    try:
        repo = github.get_repo(repo_name)
        if branch_name == repo.default_branch:
            raise ValueError(f"Refusing to publish directly to default branch '{repo.default_branch}'. Use a feature branch.")
        ref = repo.get_git_ref(f"heads/{branch_name}")
        parent = repo.get_commit(ref.object.sha)
        tree_response = repo.get_git_tree(parent.commit.tree.sha, recursive=True)
        if tree_response.truncated:
            raise ValueError("GitHub returned a truncated repository tree; refusing to risk overwriting files.")
        target_prefix = safe_target_prefix("generated/character-layers/{character_id}", char_id)
        entries = collect_publish_files(asset_dir)
        existing_paths = {entry.path for entry in tree_response.tree}
        collisions = [f"{target_prefix}/{relative}" for _, relative in entries if f"{target_prefix}/{relative}" in existing_paths]
        if collisions:
            raise FileExistsError("Refusing to replace existing repository path(s): " + ", ".join(collisions))

        elements = []
        for local_path, relative in entries:
            raw = local_path.read_bytes()
            blob = repo.create_git_blob(base64.b64encode(raw).decode("ascii"), "base64")
            elements.append(InputGitTreeElement(path=f"{target_prefix}/{relative}", mode="100644", type="blob", sha=blob.sha))
        tree = repo.create_git_tree(elements, base_tree=parent.commit.tree)
        commit = repo.create_git_commit(message, tree, [parent])
        ref.edit(commit.sha, force=False)
        return commit.html_url
    finally:
        github.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repository as OWNER/NAME.")
    parser.add_argument("--branch", required=True, help="Existing non-default branch to update.")
    parser.add_argument("--asset-dir", required=True, type=Path, help="Reviewed local folder containing PNGs/manifest/contact sheet.")
    parser.add_argument("--character-id", required=True, choices=("pibara", "sunna", "chie"))
    parser.add_argument("--message", default="Add reviewed character layer assets", help="Git commit message.")
    args = parser.parse_args()
    try:
        url = publish(args.repo, args.branch, args.asset_dir, args.character_id, args.message)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print(f"Published reviewed assets to feature branch. Commit: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
