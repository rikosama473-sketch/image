"""Regression tests for shared navigation across the IMAGE studio tools."""
from __future__ import annotations

import posixpath
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PAGES = {
    "constructor": "tools/avatar-maker/index.html",
    "library": "tools/visual-reference-library/index.html",
    "hairstyles": "tools/hairstyle-workbench/index.html",
    "manual_editor": "tools/manual-character-editor/index.html",
}
LOCAL_GENERATOR = "http://127.0.0.1:8765/"
SHARED_SERVER = "http://127.0.0.1:8766/"


class StudioNavParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_studio_nav = False
        self.nav_count = 0
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "nav" and "data-image-studio-nav" in values:
            self.in_studio_nav = True
            self.nav_count += 1
        elif self.in_studio_nav and tag == "a":
            href = values.get("href")
            if href:
                self.hrefs.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_studio_nav:
            self.in_studio_nav = False


class StudioNavigationTests(unittest.TestCase):
    def read_nav(self, relative_path: str) -> StudioNavParser:
        path = REPO_ROOT / relative_path
        self.assertTrue(path.is_file(), f"Falta el módulo: {relative_path}")
        parser = StudioNavParser()
        parser.feed(path.read_text(encoding="utf-8"))
        self.assertEqual(parser.nav_count, 1, f"{relative_path} debe tener una navegación IMAGE única")
        if relative_path != "tools/image-creator/index.html":
            self.assertIn(LOCAL_GENERATOR, parser.hrefs, f"{relative_path} debe enlazar al generador local opcional")
        return parser

    def test_local_modules_link_to_every_other_module_with_resolvable_paths(self) -> None:
        expected = set(TOOL_PAGES.values())
        for current_name, relative_path in TOOL_PAGES.items():
            with self.subTest(module=current_name):
                parser = self.read_nav(relative_path)
                resolved = {
                    posixpath.normpath(posixpath.join(posixpath.dirname(relative_path), href))
                    for href in parser.hrefs
                    if href.startswith("../")
                }
                self.assertEqual(resolved, expected - {relative_path})

    def test_inference_ui_links_back_to_the_shared_tools_server(self) -> None:
        path = "tools/image-creator/index.html"
        parser = self.read_nav(path)
        expected = {SHARED_SERVER + relative_path for relative_path in TOOL_PAGES.values()}
        self.assertTrue(expected.issubset(set(parser.hrefs)))

    def test_manual_editor_standalone_server_uses_repository_root_for_relative_links(self) -> None:
        launcher = (REPO_ROOT / "tools/manual-character-editor/run_editor.py").read_text(encoding="utf-8")
        self.assertIn("ROOT = Path(__file__).resolve().parents[2]", launcher)
        self.assertIn('INDEX = ROOT / "tools" / "manual-character-editor" / "index.html"', launcher)
        self.assertIn("/tools/manual-character-editor/index.html", launcher)


if __name__ == "__main__":
    unittest.main()
