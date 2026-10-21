#!/usr/bin/env python3
"""Validate the standalone manual editor's HTML controls and inline JavaScript syntax."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_HTML = Path(__file__).resolve().parents[1] / "tools" / "manual-character-editor" / "index.html"
REQUIRED_IDS = {
    "openImageBtn", "sampleBtn", "imageFile", "projectFile", "viewCanvas", "overlayCanvas",
    "brushSize", "tolerance", "subtractSelection", "invertSelectionBtn", "clearSelectionBtn",
    "exportSelectionBtn", "deleteSelectionBtn", "removeBgBtn", "layers", "extractLayerBtn",
    "newLayerBtn", "exportLayerBtn", "cropCanvasBtn", "saveProjectBtn", "exportCompositeBtn",
}
REQUIRED_FUNCTIONS = (
    "function extractLayer(", "function importCharacterCreatorProject(", "function importHairstyleWorkbenchProject(", "function projectImageSource(", "function checkImportedLayerBudget(", "function removeEdgeBackground(", "function floodMaskFromPixel(",
    "function cropCanvas(", "function saveProject(", "function exportLayer(",
    'requestedName!==source.name?requestedName:"Recorte "+(doc.layers.length)',
    'const name=requestedName&&(!current||requestedName!==current.name)?requestedName:"Capa nueva "+(doc.layers.length+1)',
)


class MarkupInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag.lower() == "script" and "src" not in values:
            self.scripts += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args()
    if not args.html.is_file():
        print(f"HTML file not found: {args.html}", file=sys.stderr)
        return 1
    html = args.html.read_text(encoding="utf-8")
    inspector = MarkupInspector()
    inspector.feed(html)
    duplicates = sorted({item for item in inspector.ids if inspector.ids.count(item) > 1})
    missing = sorted(REQUIRED_IDS - set(inspector.ids))
    if duplicates or missing:
        if duplicates:
            print("Duplicate element IDs: " + ", ".join(duplicates), file=sys.stderr)
        if missing:
            print("Missing required controls: " + ", ".join(missing), file=sys.stderr)
        return 1

    inline_scripts = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script\s*>", html, re.IGNORECASE)
    script = "\n".join(s for s in inline_scripts if s.strip())
    if not script or inspector.scripts == 0:
        print("No inline application script found.", file=sys.stderr)
        return 1
    missing_functions = [name for name in REQUIRED_FUNCTIONS if name not in script]
    if missing_functions:
        print("Missing editor functions: " + ", ".join(missing_functions), file=sys.stderr)
        return 1

    node = shutil.which("node")
    if not node:
        print("Node.js is required for the JavaScript syntax check.", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="image-manual-editor-") as tmp:
        js_path = Path(tmp) / "editor.js"
        js_path.write_text(script, encoding="utf-8")
        result = subprocess.run([node, "--check", str(js_path)], text=True, capture_output=True, check=False)
    if result.returncode:
        print(result.stdout + result.stderr, file=sys.stderr)
        return result.returncode
    print(f"PASS: {args.html} — {len(inspector.ids)} unique IDs, inline JavaScript syntax valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
