#!/usr/bin/env python3
"""Launch the IMAGE manual editor on loopback using only Python's standard library."""
from __future__ import annotations

import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "tools" / "manual-character-editor" / "index.html"


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep the terminal quiet; the UI reports editing errors and status.
        return


def main() -> int:
    if not INDEX.is_file():
        raise SystemExit(f"Editor HTML not found: {INDEX}")
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    host, port = server.server_address
    url = f"http://{host}:{port}/tools/manual-character-editor/index.html"
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    print("IMAGE Manual Character Editor")
    print(f"URL: {url}")
    print("The server listens only on this computer. Press Ctrl+C to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEditor stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
