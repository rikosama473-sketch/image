#!/usr/bin/env python3
"""Local-only image editing bridge for IMAGE Character Creator.

Reads OPENAI_API_KEY from the process environment. The browser never receives
or stores the provider key. This server intentionally binds to loopback only.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
API_URL = "https://api.openai.com/v1/images/edits"
ALLOWED_MODELS = {
    "gpt-image-2.5-sunburst",
    "gpt-image-2.5-flare",
    "gpt-image-2",
    "gpt-image-1.5",
}
ALLOWED_QUALITIES = {"low", "medium", "high"}
ALLOWED_BACKGROUNDS = {"auto", "opaque", "transparent"}
MAX_BODY_BYTES = 42 * 1024 * 1024
MAX_DATA_URL_CHARS = 20_000_000
DATA_URL_PATTERN = re.compile(r"^data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=\r\n]+)$")


def validate_data_url(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) > MAX_DATA_URL_CHARS:
        raise ValueError(f"{label}: falta una imagen válida o supera el límite permitido.")
    match = DATA_URL_PATTERN.fullmatch(value)
    if not match:
        raise ValueError(f"{label}: solo se admiten imágenes PNG, JPEG o WebP en base64.")
    try:
        decoded = base64.b64decode(match.group(2), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"{label}: los datos de imagen están dañados.") from exc
    if not decoded:
        raise ValueError(f"{label}: la imagen está vacía.")
    return value


class Handler(SimpleHTTPRequestHandler):
    server_version = "IMAGE-LocalAI/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/api/status":
            self.send_json(200, {
                "service": "IMAGE local AI edit bridge",
                "api_key_configured": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
                "models": sorted(ALLOWED_MODELS),
                "key_storage": "environment_only",
            })
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/ai-edit":
            self.send_json(404, {"error": "Ruta no encontrada."})
            return

        host = self.headers.get("Host", "")
        if not (host.startswith("127.0.0.1:") or host.startswith("localhost:")):
            self.send_json(403, {"error": "El servicio solo acepta conexiones locales."})
            return
        origin = self.headers.get("Origin")
        if origin:
            try:
                if urlsplit(origin).netloc != host:
                    self.send_json(403, {"error": "Origen rechazado por seguridad."})
                    return
            except ValueError:
                self.send_json(403, {"error": "Origen inválido."})
                return

        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            self.send_json(503, {
                "error": "Falta OPENAI_API_KEY en el entorno de Windows. Consultá AI_EDITING.md; la clave nunca se escribe en el repositorio."
            })
            return

        try:
            size_header = self.headers.get("Content-Length", "")
            if not size_header.isdigit():
                raise ValueError("La petición no tiene un tamaño válido.")
            size = int(size_header)
            if size <= 0 or size > MAX_BODY_BYTES:
                raise ValueError("La petición supera el límite local de 42 MiB.")
            body = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("El contenido de la petición no es válido.")

            prompt = body.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 32000:
                raise ValueError("Escribí una instrucción de edición de entre 1 y 32.000 caracteres.")

            model = body.get("model", "gpt-image-2.5-sunburst")
            if model not in ALLOWED_MODELS:
                raise ValueError("Modelo no permitido por el editor.")
            quality = body.get("quality", "medium")
            if quality not in ALLOWED_QUALITIES:
                raise ValueError("La calidad debe ser low, medium o high.")
            background = body.get("background", "auto")
            if background not in ALLOWED_BACKGROUNDS:
                raise ValueError("El fondo debe ser auto, opaque o transparent.")

            images = [{
                "image_url": validate_data_url(body.get("image_data_url"), "Imagen del lienzo")
            }]
            ref = body.get("reference_data_url")
            if ref:
                images.append({"image_url": validate_data_url(ref, "Imagen de referencia")})
            if len(images) > 2:
                raise ValueError("El editor admite una imagen base y una referencia adicional.")

            # 768 x 1280 preserves the editor canvas exactly. The older 1.5 model
            # uses the standard portrait size and the browser scales it to canvas.
            output_size = "1024x1536" if model == "gpt-image-1.5" else "768x1280"
            payload = {
                "model": model,
                "images": images,
                "prompt": prompt.strip(),
                "size": output_size,
                "quality": quality,
                "background": background,
                "output_format": "png",
                "n": 1,
            }
            req = Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                method="POST",
            )
            try:
                with urlopen(req, timeout=240) as response:
                    api_result = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = "El proveedor rechazó la edición."
                try:
                    error_body = json.loads(exc.read().decode("utf-8"))
                    detail = error_body.get("error", {}).get("message") or detail
                except (ValueError, UnicodeDecodeError, AttributeError):
                    pass
                self.send_json(exc.code if 400 <= exc.code < 500 else 502, {"error": str(detail)[:1200]})
                return
            except URLError as exc:
                self.send_json(502, {"error": "No se pudo conectar con el servicio de imágenes. Revisá la conexión y volvé a intentar."})
                return
            except TimeoutError:
                self.send_json(504, {"error": "La edición superó el tiempo de espera. Podés probar calidad media o baja."})
                return

            data = api_result.get("data") or []
            image_base64 = data[0].get("b64_json") if data and isinstance(data[0], dict) else None
            if not isinstance(image_base64, str) or not image_base64:
                self.send_json(502, {"error": "El proveedor terminó la solicitud, pero no devolvió una imagen PNG."})
                return
            self.send_json(200, {
                "image_base64": image_base64,
                "model": model,
                "quality": quality,
                "size_requested": output_size,
                "background": background,
                "usage": api_result.get("usage"),
            })
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self.send_json(400, {"error": str(exc)[:1000]})
        except Exception as exc:
            print("AI edit request failed: " + type(exc).__name__, file=sys.stderr)
            self.send_json(500, {"error": "Error inesperado del puente local. Consultá la terminal y no compartas claves API."})


def main() -> int:
    parser = argparse.ArgumentParser(description="IMAGE Character Creator: local AI image editor")
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "localhost"])
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("--port debe estar entre 1024 y 65535")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("IMAGE Character Creator en http://127.0.0.1:{}/tools/avatar-maker/index.html".format(args.port))
    print("Puente de IA: {}".format("configurado" if os.environ.get("OPENAI_API_KEY", "").strip() else "sin OPENAI_API_KEY (modo manual disponible)"))
    print("La clave se lee solo del entorno y no se guarda en los archivos.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando IMAGE Character Creator.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
