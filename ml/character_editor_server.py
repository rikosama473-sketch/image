#!/usr/bin/env python3
"""Serve IMAGE's local, offline-first modular character editor."""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EDITOR_ROOT = ROOT / "tools" / "character-editor"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".cache", ".pytest_cache", ".mypy_cache", "outputs", "checkpoints",
}
MAX_INDEXED_IMAGES = 10000
MAX_SCANNED_DIRS = 5000
MAX_IMAGE_BYTES = 100 * 1024 * 1024


class AssetCatalog:
    """A read-only, bounded index of images below one user-selected folder."""

    def __init__(self, root: Path):
        expanded = root.expanduser()
        if not expanded.exists() or not expanded.is_dir() or expanded.is_symlink():
            raise ValueError("Carpeta de imágenes no válida: " + str(expanded))
        self.root = expanded.resolve()
        self.items: list[dict[str, Any]] = []
        self.truncated = False
        self.skipped_large = 0
        self.scanned_dirs = 0
        self._scan()

    def _scan(self) -> None:
        for current, directories, filenames in os.walk(self.root, topdown=True, followlinks=False):
            folder = Path(current)
            directories[:] = sorted(
                name for name in directories
                if name not in IGNORED_DIRS
                and not name.startswith(".")
                and not (folder / name).is_symlink()
            )
            self.scanned_dirs += 1
            if self.scanned_dirs > MAX_SCANNED_DIRS:
                self.truncated = True
                break
            for filename in filenames:
                path = folder / filename
                if path.suffix.lower() not in IMAGE_EXTENSIONS or path.is_symlink():
                    continue
                try:
                    size = path.stat().st_size
                    if size > MAX_IMAGE_BYTES:
                        self.skipped_large += 1
                        continue
                    resolved = path.resolve(strict=True)
                    relative = resolved.relative_to(self.root).as_posix()
                except (OSError, ValueError):
                    continue
                self.items.append({
                    "path": relative,
                    "name": path.name,
                    "size": size,
                    "extension": path.suffix.lower().lstrip("."),
                })
                if len(self.items) >= MAX_INDEXED_IMAGES:
                    self.truncated = True
                    break
            if self.truncated:
                break
        self.items.sort(key=lambda item: item["path"].casefold())

    def list_assets(self, query: str = "", offset: int = 0, limit: int = 48) -> dict[str, Any]:
        query = query.strip().casefold()
        if len(query) > 200:
            raise ValueError("La búsqueda no puede superar 200 caracteres.")
        if offset < 0 or offset > MAX_INDEXED_IMAGES:
            raise ValueError("El desplazamiento de la galería no es válido.")
        if limit < 1 or limit > 96:
            raise ValueError("El tamaño de página debe estar entre 1 y 96.")
        matched = [
            item for item in self.items
            if not query or query in item["name"].casefold() or query in item["path"].casefold()
        ]
        return {
            "root_label": self.root.name or str(self.root),
            "items": matched[offset:offset + limit],
            "total": len(matched),
            "offset": offset,
            "limit": limit,
            "truncated": self.truncated,
            "skipped_large": self.skipped_large,
        }

    def safe_path(self, relative: str) -> Path | None:
        if not relative or "\x00" in relative:
            return None
        candidate_input = Path(relative)
        if candidate_input.is_absolute() or ".." in candidate_input.parts:
            return None
        try:
            candidate = self.root / candidate_input
            if candidate.is_symlink():
                return None
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(self.root)
            if not resolved.is_file() or resolved.suffix.lower() not in IMAGE_EXTENSIONS:
                return None
            if resolved.stat().st_size > MAX_IMAGE_BYTES:
                return None
            return resolved
        except (OSError, ValueError):
            return None


class CharacterEditorHandler(BaseHTTPRequestHandler):
    server_version = "IMAGE-CharacterEditor/0.1"

    @property
    def catalog(self) -> AssetCatalog:
        return self.server.catalog  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        print("[IMAGE Character Editor] " + (format % args))

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            return self._serve_file(EDITOR_ROOT / "index.html")
        if parsed.path in {"/app.js", "/app.css"}:
            return self._serve_file(EDITOR_ROOT / parsed.path.lstrip("/"))

        if parsed.path == "/api/assets":
            params = parse_qs(parsed.query, keep_blank_values=True)
            try:
                query = params.get("query", [""])[0]
                offset = int(params.get("offset", ["0"])[0])
                limit = int(params.get("limit", ["48"])[0])
                return self._json_response(200, self.catalog.list_assets(query, offset, limit))
            except (TypeError, ValueError) as exc:
                return self._json_response(400, {"error": str(exc)})

        if parsed.path == "/api/asset":
            relative = parse_qs(parsed.query, keep_blank_values=True).get("path", [""])[0]
            path = self.catalog.safe_path(relative)
            if path is None:
                return self._json_response(404, {"error": "No se encontró una imagen dentro de la carpeta seleccionada."})
            return self._serve_file(path)

        return self._json_response(404, {"error": "Ruta no encontrada."})

    def do_POST(self) -> None:
        self._json_response(405, {"error": "Este editor no acepta subidas ni escrituras remotas; los archivos fuente se mantienen intactos."})

    def _json_response(self, status: int, value: Any) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: Path) -> None:
        try:
            content = path.read_bytes()
        except OSError:
            return self._json_response(404, {"error": "Archivo de la interfaz no encontrado."})
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


class CharacterEditorHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], catalog: AssetCatalog):
        super().__init__(address, CharacterEditorHandler)
        self.catalog = catalog



def run_self_test() -> int:
    """Small smoke test used by the portable Windows build; no model or images are loaded."""
    required = (EDITOR_ROOT / "index.html", EDITOR_ROOT / "app.js", EDITOR_ROOT / "app.css")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("Faltan archivos incluidos en el paquete: " + ", ".join(missing))
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="image-editor-self-test-") as directory:
            sample = Path(directory) / "sample.png"
            sample.write_bytes(b"local editor smoke-test fixture")
            catalog = AssetCatalog(Path(directory))
            record = catalog.list_assets(limit=10)
            found = catalog.safe_path("sample.png")
            if len(record["items"]) != 1 or found is None or found.read_bytes() != sample.read_bytes():
                print("Falló la prueba de inventario local.")
                return 2
    except (OSError, ValueError) as exc:
        print("Falló la prueba local: " + str(exc))
        return 2
    print("IMAGE Character Editor self-test: OK")
    print("Interfaz incluida, inventario local y validación de rutas verificados.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", type=Path, default=None, help="Carpeta local de imágenes; se lee sin modificarla.")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--open-browser", action="store_true", help="Abrir el editor en el navegador local.")
    parser.add_argument("--self-test", action="store_true", help="Comprobar archivos del paquete y catálogo sin abrir el servidor.")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not 1024 <= args.port <= 65535:
        parser.error("--port debe estar entre 1024 y 65535.")
    if not (EDITOR_ROOT / "index.html").is_file():
        parser.error("Faltan los archivos de tools/character-editor.")
    asset_root = args.assets_dir
    if asset_root is None and getattr(sys, "frozen", False):
        try:
            import tkinter as tk
            from tkinter import filedialog
            window = tk.Tk()
            window.withdraw()
            window.attributes("-topmost", True)
            selected_folder = filedialog.askdirectory(title="Selecciona tu carpeta de imágenes")
            window.destroy()
        except Exception as exc:
            parser.error("No se pudo abrir el selector de carpetas de Windows: " + str(exc))
        if not selected_folder:
            print("No seleccionaste una carpeta. El editor se cerrará sin modificar nada.")
            return 1
        asset_root = Path(selected_folder)
    if asset_root is None:
        asset_root = ROOT
    try:
        catalog = AssetCatalog(asset_root)
    except ValueError as exc:
        parser.error(str(exc))
    server = CharacterEditorHTTPServer(("127.0.0.1", args.port), catalog)
    url = "http://127.0.0.1:" + str(args.port)
    print("IMAGE — Editor modular de personajes: " + url)
    print("Carpeta de imágenes (solo lectura): " + str(catalog.root))
    print("Imágenes indexadas: " + str(len(catalog.items)) + "; carpetas examinadas: " + str(catalog.scanned_dirs))
    if catalog.truncated:
        print("Aviso: se alcanzó un límite del inventario; usa una carpeta más específica para ver el resto.")
    if catalog.skipped_large:
        print("Imágenes omitidas por superar 100 MB: " + str(catalog.skipped_large))
    print("No se entrena ni genera con IA, no se suben imágenes y no se alteran originales.")
    print("Pulsa Ctrl+C para cerrar.")
    if args.open_browser or getattr(sys, "frozen", False):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando IMAGE Character Editor.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
