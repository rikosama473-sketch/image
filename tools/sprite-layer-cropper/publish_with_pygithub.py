#!/usr/bin/env python3
"""Publish UTF-8 text files to a GitHub branch using PyGithub.

Security: read the token only from GITHUB_TOKEN; never hard-code or print it.
This uses GitHub's Contents API, not a git clone. It never deletes remote files.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from github import Auth, Github
from github.GithubException import GithubException


EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
EXCLUDED_NAMES = {".env", ".env.local", ".env.production"}


def is_publishable(path: Path) -> bool:
    return (
        path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.parts)
        and path.name not in EXCLUDED_NAMES
        and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".zip", ".pt", ".safetensors"}
    )


def publish(repo_name: str, local_dir: Path, branch_name: str, commit_message: str) -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Define GITHUB_TOKEN como variable de entorno; no lo escribas en el código.")

    local_dir = local_dir.resolve()
    if not local_dir.is_dir():
        raise ValueError(f"No existe el directorio local: {local_dir}")

    client = Github(auth=Auth.Token(token))
    try:
        repo = client.get_repo(repo_name)
        default_branch = repo.default_branch
        try:
            repo.get_branch(branch_name)
        except GithubException as exc:
            if exc.status != 404:
                raise
            base_sha = repo.get_branch(default_branch).commit.sha
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

        published = 0
        skipped = 0
        for local_path in sorted(local_dir.rglob("*")):
            if not is_publishable(local_path):
                if local_path.is_file():
                    skipped += 1
                continue

            relative_path = local_path.relative_to(local_dir).as_posix()
            # Contents API expects text for this helper; fail loudly on binary/non-UTF-8 data.
            content = local_path.read_text(encoding="utf-8")
            try:
                remote = repo.get_contents(relative_path, ref=branch_name)
            except GithubException as exc:
                if exc.status != 404:
                    raise
                repo.create_file(
                    path=relative_path,
                    message=commit_message,
                    content=content,
                    branch=branch_name,
                )
            else:
                if isinstance(remote, list):
                    raise RuntimeError(f"La ruta remota no es un archivo: {relative_path}")
                if remote.decoded_content.decode("utf-8") == content:
                    skipped += 1
                    continue
                repo.update_file(
                    path=relative_path,
                    message=commit_message,
                    content=content,
                    sha=remote.sha,
                    branch=branch_name,
                )
            published += 1
            print(f"Publicado: {relative_path}")

        print(f"Resultado: {published} archivo(s) creados/actualizados; {skipped} omitidos.")
        print(f"Repositorio: https://github.com/{repo_name}/tree/{branch_name}")
        return published
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--directory", type=Path, required=True, help="Directorio local de archivos UTF-8")
    parser.add_argument("--branch", default="automation/sync-text-assets")
    parser.add_argument("--message", default="Sync text assets with PyGithub")
    args = parser.parse_args()
    try:
        publish(args.repo, args.directory, args.branch, args.message)
        return 0
    except (OSError, UnicodeError, ValueError, RuntimeError, GithubException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
