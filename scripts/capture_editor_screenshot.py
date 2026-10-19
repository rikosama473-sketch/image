from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "preview-output"
OUT = OUT_DIR / "IMAGE-app-character-hair-full-page.png"
SCREENSHOT_DIR = ROOT / "screenshots"
FOCUSED = SCREENSHOT_DIR / "IMAGE-app-cabello-01-captura.jpg"
PANEL_SHOT = SCREENSHOT_DIR / "IMAGE-app-edicion-animeart-panel.jpg"
FULL_REPO_SHOT = SCREENSHOT_DIR / "IMAGE-app-edicion-animeart-completo.png"
GALLERY_SHOT = SCREENSHOT_DIR / "IMAGE-app-referencias-peinados.png"
PREVIEW_COPY = OUT_DIR / "IMAGE-app-cabello-01-captura.jpg"
PANEL_COPY = OUT_DIR / "IMAGE-app-edicion-animeart-panel.jpg"
FULL_COPY = OUT_DIR / "IMAGE-app-edicion-animeart-completo.png"
GALLERY_COPY = OUT_DIR / "IMAGE-app-referencias-peinados.png"
PORT = 8766
BASE = f"http://127.0.0.1:{PORT}"


def wait_for_server(process: subprocess.Popen[str], timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"IMAGE server exited early with code {process.returncode}")
        try:
            with urllib.request.urlopen(BASE + "/", timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    raise TimeoutError("IMAGE local server did not start within 30 seconds")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install Playwright before capturing the real app screenshot.") from exc

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(OUT.parent / "editor-server.log", "w", encoding="utf-8")
    server = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "ml" / "character_editor_server.py"),
            "--assets-dir", str(ROOT),
            "--port", str(PORT),
        ],
        cwd=ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server(server)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1660, "height": 1180}, device_scale_factor=1)
            page.goto(BASE + "/", wait_until="domcontentloaded", timeout=30000)
            page.locator("#asset-grid .asset-card").first.wait_for(timeout=30000)
            search = page.locator("#asset-search")

            # Add the existing user-repository character image first.
            search.fill("12.png")
            page.locator("#asset-grid .asset-card").first.wait_for(timeout=15000)
            page.locator("#asset-grid .asset-card button").first.click()
            page.locator("#layer-list .layer-row").first.wait_for(timeout=15000)

            # Then overlay the original SVG hair piece. The source PNG is never edited.
            search.fill("cabello_01.svg")
            page.locator("#asset-grid .asset-card").first.wait_for(timeout=15000)
            page.locator("#asset-grid .asset-card button").first.click()
            page.wait_for_function(
                "() => document.querySelectorAll('#layer-list .layer-row').length >= 2",
                timeout=15000,
            )
            page.wait_for_timeout(700)
            page.locator("#layer-category").select_option("hair")
            page.wait_for_timeout(500)

            # Ensure the browser finished drawing all image layers before the capture.
            page.evaluate(
                """async () => {
                    const images = Array.from(document.images);
                    await Promise.all(images.map(image => image.complete ? Promise.resolve() :
                      new Promise(resolve => { image.addEventListener('load', resolve, {once:true});
                                               image.addEventListener('error', resolve, {once:true}); })));
                    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                }"""
            )
            # Keep a full view of the real app and focused captures of its canvas and advanced panel.
            page.screenshot(path=str(OUT), full_page=True, animations="disabled")
            page.locator("#stage").screenshot(path=str(FOCUSED), type="jpeg", quality=92, animations="disabled")
            page.locator("#pro-edit-panel").screenshot(path=str(PANEL_SHOT), type="jpeg", quality=92, animations="disabled")

            # Capture a separate, app-generated reference-gallery screenshot with the
            # 46 hairstyle thumbnails visible. Remote hosts may block individual
            # previews; failed thumbnails remain clearly marked by the UI.
            gallery = page.locator("#hair-reference-library")
            gallery.locator("summary").click()
            page.locator("#hair-reference-grid .hair-reference-card").first.wait_for(timeout=15000)
            gallery.evaluate("(node) => { node.open = true; node.scrollIntoView({block: 'start'}); }")
            page.locator("#hair-reference-grid img").evaluate_all(
                "(images) => images.forEach(image => { image.loading = 'eager'; })"
            )
            page.evaluate(
                """async () => {
                    const images = Array.from(document.querySelectorAll("#hair-reference-grid img"));
                    await Promise.race([
                      Promise.all(images.map(image => new Promise(resolve => {
                        if (image.complete) return resolve();
                        const done = () => resolve();
                        image.addEventListener("load", done, {once: true});
                        image.addEventListener("error", done, {once: true});
                      }))),
                      new Promise(resolve => setTimeout(resolve, 9000))
                    ]);
                    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                }"""
            )
            gallery.screenshot(path=str(GALLERY_SHOT), animations="disabled", timeout=30000)
            browser.close()

        shutil.copy2(OUT, FULL_REPO_SHOT)
        shutil.copy2(FOCUSED, PREVIEW_COPY)
        shutil.copy2(PANEL_SHOT, PANEL_COPY)
        shutil.copy2(FULL_REPO_SHOT, FULL_COPY)
        shutil.copy2(GALLERY_SHOT, GALLERY_COPY)

        print(json.dumps({
            "full_app_screenshot": str(FULL_REPO_SHOT.relative_to(ROOT)),
            "canvas_screenshot": str(FOCUSED.relative_to(ROOT)),
            "advanced_editor_panel": str(PANEL_SHOT.relative_to(ROOT)),
            "hairstyle_reference_gallery": str(GALLERY_SHOT.relative_to(ROOT)),
            "character_source": "12.png",
            "hair_overlay": "assets/parts/hair/cabello_01.svg",
            "layers": 2,
            "source_modified": False,
        }, ensure_ascii=False))
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
        log_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
