#!/usr/bin/env python3
"""Validate KIRA's standalone HTML controls and inline JavaScript syntax."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parents[1] / "tools" / "avatar-maker" / "index.html"
REQUIRED_IDS = {
    "randomBtn", "resetBtn", "saveBtn", "loadBtn", "projectFile", "partFile",
    "avatarMount", "nameChip", "characterName", "panel", "pngBtn", "svgBtn",
    "uploadPartBtn", "clearPartsBtn", "pieceList", "pieceEmpty",
}
REQUIRED_FEATURES = (
    "function renderSvg(", "function renderPanel(", "function renderPieces(",
    "function addPiece(", "function exportPng(", "function exportSvg(",
    "function saveProject(", "function loadProject(",
    "data-part-id", "KIRA Avatar Maker",
)


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.inline_script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if attrs_map.get("id"):
            self.ids.append(attrs_map["id"])
        if tag.lower() == "script" and "src" not in attrs_map:
            self.inline_script_count += 1


def main() -> int:
    if not HTML_PATH.is_file():
        print(f"Missing avatar maker HTML: {HTML_PATH}", file=sys.stderr)
        return 1
    html = HTML_PATH.read_text(encoding="utf-8")
    inspector = Inspector()
    inspector.feed(html)
    duplicates = sorted({element_id for element_id in inspector.ids if inspector.ids.count(element_id) > 1})
    missing = sorted(REQUIRED_IDS - set(inspector.ids))
    features_missing = [feature for feature in REQUIRED_FEATURES if feature not in html]
    if duplicates or missing or features_missing:
        if duplicates:
            print("Duplicate HTML IDs: " + ", ".join(duplicates), file=sys.stderr)
        if missing:
            print("Required controls missing: " + ", ".join(missing), file=sys.stderr)
        if features_missing:
            print("Required features missing: " + ", ".join(features_missing), file=sys.stderr)
        return 1
    scripts = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script\s*>", html, re.IGNORECASE)
    inline_js = "\n".join(script for script in scripts if script.strip())
    if not inline_js or inspector.inline_script_count == 0:
        print("No inline app script found.", file=sys.stderr)
        return 1
    node = shutil.which("node")
    if not node:
        print("Node.js is required for the JavaScript syntax check.", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="kira-avatar-maker-") as temp:
        js = Path(temp) / "avatar-maker.js"
        js.write_text(inline_js, encoding="utf-8")
        proc = subprocess.run([node, "--check", str(js)], text=True, capture_output=True, check=False)
    if proc.returncode:
        print(proc.stdout + proc.stderr, file=sys.stderr)
        return proc.returncode
    print(f"PASS: {HTML_PATH.name}: {len(inspector.ids)} IDs, required features present, JavaScript syntax valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
