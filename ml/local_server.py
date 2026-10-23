#!/usr/bin/env python3
"""Serve the local IMAGE creator UI and launch the local Diffusers engine.

The server binds only to loopback. Generation is performed by a local Python
subprocess; the UI does not upload images or contact a remote inference API.
"""
from __future__ import annotations

import importlib.util
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "tools" / "image-creator"
ENGINE = ROOT / "ml" / "generate_diffusion.py"
OUTPUT_ROOT = ROOT / "outputs" / "generated"
MAX_BODY_BYTES = 64 * 1024
MAX_PROMPT_CHARS = 8000
MAX_JOBS_IN_MEMORY = 80
JOBS: dict[str, dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()
JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def _json_response(handler: BaseHTTPRequestHandler, status: int, value: Any) -> None:
    body = json.dumps(value, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _safe_output_path(relative: str) -> Path | None:
    candidate = (OUTPUT_ROOT / relative).resolve()
    root = OUTPUT_ROOT.resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def _list_outputs(limit: int = 30) -> list[dict[str, Any]]:
    if not OUTPUT_ROOT.exists():
        return []
    files = sorted(OUTPUT_ROOT.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    results: list[dict[str, Any]] = []
    for path in files[:limit]:
        try:
            relative = path.relative_to(OUTPUT_ROOT).as_posix()
            sidecar = path.with_suffix(".json")
            metadata: dict[str, Any] = {}
            if sidecar.is_file():
                try:
                    data = json.loads(sidecar.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        metadata = data
                except (OSError, json.JSONDecodeError):
                    metadata = {}
            results.append({
                "path": relative,
                "url": "/generated/" + relative,
                "prompt": metadata.get("prompt", ""),
                "model": metadata.get("model", ""),
                "lora": metadata.get("lora") or "",
                "seed": metadata.get("seed", ""),
                "mtime": int(path.stat().st_mtime),
            })
        except OSError:
            continue
    return results


def _model_search_roots() -> list[tuple[Path, str]]:
    """Return bounded, explicit locations where local Diffusers pipelines may live."""
    roots: list[tuple[Path, str]] = [
        (ROOT / "models", "project"),
        (ROOT / "outputs" / "models", "project"),
    ]
    cache_override = os.environ.get("HUGGINGFACE_HUB_CACHE", "").strip()
    if cache_override:
        roots.append((Path(cache_override).expanduser(), "huggingface-cache"))
    else:
        hf_home = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))).expanduser()
        roots.append((hf_home / "hub", "huggingface-cache"))
        # Keep the conventional cache as fallback if HF_HOME points elsewhere.
        roots.append((Path.home() / ".cache" / "huggingface" / "hub", "huggingface-cache"))

    unique: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for root, source in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        key = str(resolved).casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append((resolved, source))
    return unique


def _scan_local_models(max_directories: int = 12000, max_models: int = 100) -> dict[str, Any]:
    """Find local Diffusers pipeline folders without loading weights or contacting a hub."""
    models: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    scanned = 0
    truncated = False
    skipped_roots: list[str] = []

    for root, source in _model_search_roots():
        if not root.is_dir():
            continue
        if not os.access(root, os.R_OK):
            skipped_roots.append(str(root))
            continue
        for current, dirnames, filenames in os.walk(root, followlinks=False):
            scanned += 1
            if scanned > max_directories or len(models) >= max_models:
                truncated = True
                break
            # Do not follow symlinks or dive into common cache/metadata directories.
            dirnames[:] = sorted(
                name for name in dirnames
                if name not in {".git", "node_modules", "__pycache__"}
                and not (Path(current) / name).is_symlink()
            )
            if "model_index.json" not in filenames:
                continue
            model_dir = Path(current)
            try:
                resolved = model_dir.resolve()
                marker = (resolved / "model_index.json").read_text(encoding="utf-8")
                config = json.loads(marker)
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(config, dict) or not isinstance(config.get("_class_name"), str):
                continue
            class_name = config["_class_name"].strip()
            if not class_name:
                continue
            canonical = str(resolved).casefold()
            if canonical in seen_paths:
                continue
            seen_paths.add(canonical)

            label = str(resolved)
            model_source = source
            if source == "project":
                try:
                    label = resolved.relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    # Temporary/external search roots still get a concise human label.
                    label = resolved.name
            else:
                match = re.search(r"models--([^/\\]+)[/\\]snapshots[/\\]([^/\\]+)", str(resolved))
                if match:
                    repository_id = match.group(1).replace("--", "/")
                    label = repository_id + " · caché " + match.group(2)[:8]
                model_source = "huggingface-cache"
            models.append({
                "path": str(resolved),
                "label": label,
                "source": model_source,
                "pipeline_class": class_name[:120],
            })
        if truncated:
            break

    models.sort(key=lambda item: (item["source"] != "project", item["label"].casefold()))
    return {
        "models": models,
        "count": len(models),
        "scanned_directories": min(scanned, max_directories),
        "truncated": truncated,
        "skipped_roots": skipped_roots,
        "downloads_performed": False,
        "weights_loaded": False,
    }


def _module_available(name: str) -> bool:
    """Check dependencies without importing a large machine-learning runtime."""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError, AttributeError):
        return False


def _diagnose_environment(model: str = "", lora: str = "", device: str = "auto", allow_download: bool = False) -> dict[str, Any]:
    """Inspect prerequisites without loading weights, generating or downloading."""
    dependencies = {name: _module_available(name) for name in ("torch", "diffusers", "safetensors")}
    if device not in {"auto", "cpu", "cuda", "mps"}:
        device = "auto"
    model_value = model.strip()
    model_path = Path(model_value).expanduser() if model_value else None
    if not model_value:
        model_state, model_ready = "missing", False
        model_message = "Indicá una carpeta local de Diffusers o un identificador de modelo."
    elif model_path and model_path.is_absolute() and model_path.is_file():
        model_state, model_ready = "single_file_unsupported", False
        model_message = "Elegí una carpeta de pipeline Diffusers; un checkpoint suelto no se acepta como carpeta de modelo."
    elif model_path and model_path.is_dir():
        if (model_path / "model_index.json").is_file():
            model_state, model_ready = "local_directory_ready", True
            model_message = "La carpeta contiene model_index.json; está lista para intentar cargarla."
        else:
            model_state, model_ready = "directory_without_pipeline_config", False
            model_message = "La carpeta no contiene model_index.json; puede no ser un pipeline Diffusers completo."
    elif model_value.startswith((".", "~")) or Path(model_value).suffix:
        model_state, model_ready = "path_not_found", False
        model_message = "No existe esa ruta local. Si usás un identificador de Hub, escribilo como organización/modelo."
    elif allow_download:
        model_state, model_ready = "hub_identifier_download_enabled", True
        model_message = "Se intentará resolver el identificador y descargar pesos porque habilitaste esa opción."
    else:
        model_state, model_ready = "hub_identifier_or_cached_model", False
        model_message = "No se encontró una carpeta local. Un identificador de Hub podría funcionar si ya está en caché; no se descargará nada."
    lora_value = lora.strip()
    if not lora_value:
        lora_state, lora_message = "not_configured", "La LoRA es opcional y no está configurada."
    else:
        lora_path = Path(lora_value).expanduser()
        if lora_path.is_file():
            lora_state, lora_message = "local_file", "Archivo LoRA local encontrado; su compatibilidad se revisa al cargar."
        elif lora_path.is_dir():
            lora_state, lora_message = "local_directory", "Carpeta LoRA local encontrada; su compatibilidad se revisa al cargar."
        else:
            lora_state, lora_message = "not_found_or_hub_id", "No se encontró una ruta local para la LoRA; revisá caché y descargas si usás un identificador remoto."
    engine_exists = ENGINE.is_file()
    return {
        "python_version": sys.version.split()[0], "platform": sys.platform,
        "engine_exists": engine_exists, "dependencies": dependencies,
        "dependencies_ready": all(dependencies.values()) and engine_exists,
        "model": {"state": model_state, "ready_to_try": model_ready, "message": model_message},
        "lora": {"state": lora_state, "message": lora_message},
        "device_requested": device,
        "device_note": "La disponibilidad CUDA/MPS y el consumo de memoria no se miden aquí; el motor los verifica al iniciar.",
        "allow_download": bool(allow_download), "downloads_default_off": True, "inference_started": False,
    }


def _validate_payload(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON.")
    prompt = data.get("prompt", "")
    model = data.get("model", "")
    negative_prompt = data.get("negative_prompt", "")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Escribe una descripción de la imagen.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError(f"La descripción no puede superar {MAX_PROMPT_CHARS} caracteres.")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("Indica una carpeta de modelo compatible.")
    if len(model) > 2048 or not isinstance(negative_prompt, str) or len(negative_prompt) > MAX_PROMPT_CHARS:
        raise ValueError("El modelo o el prompt superan el límite permitido.")
    lora = data.get("lora", "")
    weight_name = data.get("lora_weight_name", "")
    if not isinstance(lora, str) or len(lora) > 2048:
        raise ValueError("La ruta de LoRA no es válida.")
    if not isinstance(weight_name, str) or len(weight_name) > 512:
        raise ValueError("El nombre de archivo de LoRA no es válido.")

    def integer(key: str, default: int, low: int, high: int) -> int:
        value = data.get(key, default)
        if isinstance(value, bool):
            raise ValueError(f"{key} debe ser un número entero.")
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{key} debe ser un número entero.") from exc
        if value < low or value > high:
            raise ValueError(f"{key} debe estar entre {low} y {high}.")
        return value

    def number(key: str, default: float, low: float, high: float) -> float:
        value = data.get(key, default)
        if isinstance(value, bool):
            raise ValueError(f"{key} debe ser un número.")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{key} debe ser un número.") from exc
        if not (low <= value <= high):
            raise ValueError(f"{key} debe estar entre {low} y {high}.")
        return value

    device = data.get("device", "auto")
    precision = data.get("precision", "auto")
    if device not in {"auto", "cpu", "cuda", "mps"}:
        raise ValueError("Dispositivo no válido.")
    if precision not in {"auto", "fp16", "bf16", "fp32"}:
        raise ValueError("Precisión no válida.")
    allow_download = data.get("allow_download", False)
    cpu_offload = data.get("cpu_offload", False)
    low_memory = data.get("low_memory", True)
    if not all(isinstance(flag, bool) for flag in (allow_download, cpu_offload, low_memory)):
        raise ValueError("Las opciones de memoria/descarga deben ser booleanas.")
    width = integer("width", 512, 64, 2048)
    height = integer("height", 512, 64, 2048)
    if width % 8 or height % 8:
        raise ValueError("El ancho y el alto deben ser múltiplos de ocho.")
    return {
        "model": model.strip(),
        "lora": lora.strip(),
        "lora_weight_name": weight_name.strip(),
        "prompt": prompt.strip(),
        "negative_prompt": negative_prompt.strip(),
        "width": width,
        "height": height,
        "steps": integer("steps", 20, 1, 150),
        "guidance_scale": number("guidance_scale", 7.0, 0, 40),
        "seed": integer("seed", 7, 0, 2**32 - 1),
        "count": integer("count", 1, 1, 8),
        "lora_scale": number("lora_scale", 0.8, 0, 2),
        "device": device,
        "precision": precision,
        "allow_download": allow_download,
        "cpu_offload": cpu_offload,
        "low_memory": low_memory,
    }


def _build_command(config: dict[str, Any], job_dir: Path) -> list[str]:
    command = [
        sys.executable, str(ENGINE),
        "--model", config["model"],
        "--prompt", config["prompt"],
        "--negative-prompt", config["negative_prompt"],
        "--width", str(config["width"]),
        "--height", str(config["height"]),
        "--steps", str(config["steps"]),
        "--guidance-scale", str(config["guidance_scale"]),
        "--seed", str(config["seed"]),
        "--count", str(config["count"]),
        "--lora-scale", str(config["lora_scale"]),
        "--device", config["device"],
        "--precision", config["precision"],
        "--output-dir", str(job_dir),
    ]
    if config["lora"]:
        command.extend(["--lora", config["lora"]])
    if config["lora_weight_name"]:
        command.extend(["--lora-weight-name", config["lora_weight_name"]])
    if config["allow_download"]:
        command.append("--allow-download")
    if config["cpu_offload"]:
        command.append("--cpu-offload")
    command.append("--low-memory" if config["low_memory"] else "--no-low-memory")
    return command


def _run_job(job_id: str, config: dict[str, Any], job_dir: Path) -> None:
    command = _build_command(config, job_dir)
    with JOBS_LOCK:
        JOBS[job_id]["status"] = "running"
        JOBS[job_id]["started_at"] = time.time()
        JOBS[job_id]["output_dir"] = str(job_dir.relative_to(OUTPUT_ROOT))
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=24 * 60 * 60,
            check=False,
        )
        summary = (result.stdout or "")[-12000:]
        error = (result.stderr or "")[-12000:]
        # The diffusion engine creates a timestamped run directory inside job_dir.
        # Search recursively or successful generations appear to fail in the UI.
        images = []
        if job_dir.exists():
            images = [
                "/generated/" + file.relative_to(OUTPUT_ROOT).as_posix()
                for file in sorted(job_dir.rglob("*.png"))
                if file.is_file()
            ]
        expected = int(config.get("count", 1))
        succeeded = bool(images) and result.returncode == 0
        complete = succeeded and len(images) >= expected
        partial = bool(images) and not complete
        if complete:
            state = "completed"
            public_error = ""
        elif partial:
            state = "partial"
            public_error = f"El motor guardó {len(images)} de {expected} imágenes solicitadas. Revisá el registro para conocer los fallos."
        else:
            state = "failed"
            public_error = error or summary or "El motor terminó sin producir imágenes."
        with JOBS_LOCK:
            JOBS[job_id].update({
                "status": state,
                "return_code": result.returncode,
                "stdout": summary,
                "stderr": error,
                "images": images,
                "requested_count": expected,
                "finished_at": time.time(),
                "error": public_error,
            })
    except subprocess.TimeoutExpired:
        with JOBS_LOCK:
            JOBS[job_id].update({
                "status": "failed", "error": "La ejecución superó el límite de 24 horas.",
                "finished_at": time.time(),
            })
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id].update({
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "finished_at": time.time(),
            })


class CreatorHandler(BaseHTTPRequestHandler):
    server_version = "IMAGE-LocalCreator/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        print("[IMAGE UI] " + (format % args))

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            return self._serve_file(UI_ROOT / "index.html")
        if parsed.path in {"/app.js", "/app.css"}:
            return self._serve_file(UI_ROOT / parsed.path.lstrip("/"))
        if parsed.path == "/api/models":
            return _json_response(self, 200, _scan_local_models())
        if parsed.path == "/api/diagnostics":
            query = parse_qs(parsed.query)
            model = query.get("model", [""])[0][:2048]
            lora = query.get("lora", [""])[0][:2048]
            device = query.get("device", ["auto"])[0]
            allow_download = query.get("allow_download", ["false"])[0].lower() in {"1", "true", "yes"}
            return _json_response(self, 200, _diagnose_environment(model, lora, device, allow_download))
        if parsed.path == "/api/runs":
            return _json_response(self, 200, {"runs": _list_outputs()})
        if parsed.path.startswith("/api/jobs/"):
            job_id = parsed.path.rsplit("/", 1)[-1]
            if not JOB_ID_RE.fullmatch(job_id):
                return _json_response(self, 400, {"error": "Identificador de trabajo no válido."})
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                snapshot = dict(job) if job else None
            if snapshot is None:
                return _json_response(self, 404, {"error": "Trabajo no encontrado."})
            return _json_response(self, 200, snapshot)
        if parsed.path.startswith("/generated/"):
            relative = unquote(parsed.path[len("/generated/"):])
            path = _safe_output_path(relative)
            if path is None or not path.is_file() or path.suffix.lower() not in {".png", ".json"}:
                return _json_response(self, 404, {"error": "Archivo de salida no encontrado."})
            return self._serve_file(path)
        return _json_response(self, 404, {"error": "Ruta no encontrada."})

    def do_POST(self) -> None:
        host = self.headers.get("Host", "")
        if host not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
            return _json_response(self, 403, {"error": "Solo se admiten solicitudes locales."})
        origin = self.headers.get("Origin")
        if origin and origin not in {
            f"http://127.0.0.1:{self.server.server_port}",
            f"http://localhost:{self.server.server_port}",
        }:
            return _json_response(self, 403, {"error": "El origen de la solicitud no es local."})
        if urlparse(self.path).path != "/api/generate":
            return _json_response(self, 404, {"error": "Ruta no encontrada."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return _json_response(self, 400, {"error": "Content-Length no válido."})
        if size <= 0 or size > MAX_BODY_BYTES:
            return _json_response(self, 413, {"error": "Tamaño de solicitud no válido."})
        try:
            raw = self.rfile.read(size)
            data = json.loads(raw.decode("utf-8"))
            config = _validate_payload(data)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            return _json_response(self, 400, {"error": str(exc)})

        with JOBS_LOCK:
            active = sum(job.get("status") in {"queued", "running"} for job in JOBS.values())
            if active:
                return _json_response(self, 409, {"error": "Ya hay una generación en curso. Espera a que finalice antes de iniciar otra."})
            finished = [key for key, job in JOBS.items() if job.get("status") not in {"queued", "running"}]
            while len(JOBS) >= MAX_JOBS_IN_MEMORY and finished:
                JOBS.pop(finished.pop(0), None)
            job_id = uuid.uuid4().hex
            # The generated directory is controlled by the server, not by request input.
            job_dir = OUTPUT_ROOT / f"ui-run-{job_id}"
            JOBS[job_id] = {"id": job_id, "status": "queued", "created_at": time.time(), "config": config}
        thread = threading.Thread(target=_run_job, args=(job_id, config, job_dir), daemon=True)
        thread.start()
        return _json_response(self, 202, {"job_id": job_id, "status": "queued"})

    def _serve_file(self, path: Path) -> None:
        try:
            content = path.read_bytes()
        except OSError:
            return _json_response(self, 404, {"error": "Archivo no encontrado."})
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Loopback only by default")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        parser.error("Por seguridad, el servidor solo puede escuchar en loopback.")
    if not 1024 <= args.port <= 65535:
        parser.error("--port debe estar entre 1024 y 65535.")
    if not ENGINE.is_file() or not (UI_ROOT / "index.html").is_file():
        parser.error("Faltan los archivos del motor o de la interfaz local.")
    server = ThreadingHTTPServer((args.host, args.port), CreatorHandler)
    print(f"IMAGE local creator: http://{args.host}:{args.port}")
    print("Solo local: las imágenes se generan en esta PC y no se suben a un servicio externo.")
    print("Pulsa Ctrl+C para cerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando IMAGE local creator.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
