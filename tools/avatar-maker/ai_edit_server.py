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
import threading
from io import BytesIO
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
ALLOWED_QUALITIES = {"low", "medium", "high", "xhigh", "max"}
PREMIUM_QUALITY_MODELS = {"gpt-image-2.5-sunburst", "gpt-image-2.5-flare"}
ALLOWED_BACKGROUNDS = {"auto", "opaque", "transparent"}
MAX_BODY_BYTES = 42 * 1024 * 1024
MAX_DATA_URL_CHARS = 20_000_000
MAX_CUTOUT_PIXELS = 20_000_000
ALLOWED_CUTOUT_MODELS = {"isnet-anime", "birefnet-portrait"}
_CUTOUT_SESSIONS = {}
_CUTOUT_LOCK = threading.Lock()
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
    image_type = match.group(1)
    signatures = {
        "png": decoded.startswith(b"\x89PNG\r\n\x1a\n"),
        "jpeg": decoded.startswith(b"\xff\xd8\xff"),
        "webp": len(decoded) >= 12 and decoded[:4] == b"RIFF" and decoded[8:12] == b"WEBP",
    }
    if not signatures.get(image_type, False):
        raise ValueError(f"{label}: el contenido no coincide con el formato declarado.")
    return value


def validate_cutout_model(value: object) -> str:
    """Only local segmentation models are accepted; no image is sent to a cloud service."""
    if not isinstance(value, str) or value not in ALLOWED_CUTOUT_MODELS:
        raise ValueError("Elegí el modelo local isnet-anime o birefnet-portrait.")
    return value


def validate_mask_data_url(value: object) -> str:
    """GPT Image edit masks must be PNG and use transparent pixels for editable areas."""
    mask_url = validate_data_url(value, "Máscara de edición")
    if not mask_url.startswith("data:image/png;base64,"):
        raise ValueError("La máscara de edición debe ser PNG con transparencia.")
    return mask_url


def validate_quality(model: object, quality: object) -> str:
    if not isinstance(quality, str) or quality not in ALLOWED_QUALITIES:
        raise ValueError("La calidad debe ser low, medium, high, xhigh o max.")
    if quality in {"xhigh", "max"} and model not in PREMIUM_QUALITY_MODELS:
        raise ValueError("La calidad xhigh/max solo está disponible para GPT Image 2.5 Sunburst y Flare.")
    return quality


def validate_variants(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 4:
        raise ValueError("Elegí entre 1 y 4 variantes por solicitud.")
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
            try:
                import importlib.util
                cutout_available = importlib.util.find_spec("rembg") is not None
            except (ImportError, ValueError):
                cutout_available = False
            self.send_json(200, {
                "service": "IMAGE local AI edit bridge",
                "api_key_configured": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
                "models": sorted(ALLOWED_MODELS),
                "local_cutout_available": cutout_available,
                "local_cutout_models": sorted(ALLOWED_CUTOUT_MODELS),
                "key_storage": "environment_only",
            })
            return
        super().do_GET()

    def do_remove_background(self) -> None:
        """Pixel-preserving, local anime cutout with cached model sessions."""
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
            model = validate_cutout_model(body.get("model", "isnet-anime"))
            input_url = validate_data_url(body.get("image_data_url"), "Imagen del lienzo")
            encoded = input_url.split(",", 1)[1]
            raw = base64.b64decode(encoded, validate=True)
            from PIL import Image, ImageOps
            with Image.open(BytesIO(raw)) as source:
                source = ImageOps.exif_transpose(source)
                source.load()
                width, height = source.size
                if width < 64 or height < 64:
                    raise ValueError("La imagen debe medir al menos 64×64 píxeles.")
                if width * height > MAX_CUTOUT_PIXELS:
                    raise ValueError("La imagen supera el límite de 20 megapíxeles para recorte local.")
                original_size = (width, height)
                normalized = source.convert("RGBA")
            normalized_buffer = BytesIO()
            normalized.save(normalized_buffer, format="PNG", optimize=True)
            try:
                from rembg import new_session, remove
            except ImportError:
                self.send_json(503, {
                    "error": "El recorte local para anime no está instalado. Ejecutá: python -m pip install -r requirements-avatar-cutout.txt. No se enviaron imágenes a la nube."
                })
                return
            with _CUTOUT_LOCK:
                session = _CUTOUT_SESSIONS.get(model)
                if session is None:
                    session = new_session(model)
                    _CUTOUT_SESSIONS[model] = session
                output = remove(
                    normalized_buffer.getvalue(),
                    session=session,
                    alpha_matting=False,
                    post_process_mask=False,
                    decontaminate=True,
                    force_return_bytes=True,
                )
            if not isinstance(output, (bytes, bytearray)) or not output:
                raise ValueError("El motor local no devolvió una imagen PNG válida.")
            with Image.open(BytesIO(bytes(output))) as cutout:
                cutout.load()
                if cutout.size != original_size:
                    raise ValueError("El motor cambió las dimensiones; se rechazó el recorte para evitar desalineación.")
                rgba = cutout.convert("RGBA")
            alpha_histogram = rgba.getchannel("A").histogram()
            transparent_pixels = sum(alpha_histogram[:255])
            if transparent_pixels <= 0:
                self.send_json(422, {"error": "El modelo no encontró píxeles transparentes. Probá otra referencia o ajustá la selección manual."})
                return
            result_buffer = BytesIO()
            rgba.save(result_buffer, format="PNG", optimize=True)
            result_bytes = result_buffer.getvalue()
            self.send_json(200, {
                "image_base64": base64.b64encode(result_bytes).decode("ascii"),
                "model": model,
                "width": rgba.width,
                "height": rgba.height,
                "transparent_pixels": transparent_pixels,
                "engine": "rembg-local",
                "source_artwork_preserved": True,
                "edge_decontamination": True,
                "review_status": "pending_visual_review",
            })
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)[:1200]})
        except Exception as exc:
            # Avoid returning request/provider internals or local paths to the browser.
            self.send_json(502, {"error": "El recorte local falló (" + type(exc).__name__ + "). Revisá la imagen o el modelo instalado; el original no se modificó."})

    def do_POST(self) -> None:
        if urlsplit(self.path).path == "/api/remove-background":
            self.do_remove_background()
            return
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
            quality = validate_quality(model, body.get("quality", "medium"))
            variants = validate_variants(body.get("variants", 1))
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

            raw_mask = body.get("mask_data_url")
            mask_payload = {"image_url": validate_mask_data_url(raw_mask)} if raw_mask else None

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
                "n": variants,
            }
            if mask_payload:
                payload["mask"] = mask_payload
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
            images_base64 = [
                item.get("b64_json")
                for item in data
                if isinstance(item, dict) and isinstance(item.get("b64_json"), str) and item.get("b64_json")
            ]
            if not images_base64:
                self.send_json(502, {"error": "El proveedor terminó la solicitud, pero no devolvió una imagen PNG."})
                return
            self.send_json(200, {
                "image_base64": images_base64[0],
                "images_base64": images_base64,
                "model": model,
                "quality": quality,
                "variants_requested": variants,
                "variants_returned": len(images_base64),
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
