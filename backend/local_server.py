from __future__ import annotations

import socket
import threading
import time

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

_server_started = False
_server_lock = threading.Lock()


def _port_open(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def start_embedded_fastapi(timeout_seconds: float = 12.0) -> tuple[str, bool]:
    """Start FastAPI inside the same Streamlit runtime and return its local URL."""
    global _server_started
    url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"
    if _port_open():
        _server_started = True
        return url, True

    with _server_lock:
        if not _port_open() and not _server_started:
            from .main import app

            config = uvicorn.Config(
                app,
                host=DEFAULT_HOST,
                port=DEFAULT_PORT,
                log_level="warning",
                access_log=False,
            )
            server = uvicorn.Server(config)

            def run() -> None:
                global _server_started
                _server_started = True
                try:
                    server.run()
                finally:
                    _server_started = False

            thread = threading.Thread(target=run, name="embedded-fastapi", daemon=True)
            thread.start()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if _port_open():
            return url, True
        time.sleep(0.2)
    return url, _port_open()
