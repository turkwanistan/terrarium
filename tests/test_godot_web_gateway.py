from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tools.godot_web_gateway import GatewayHandler, GatewayServer


class _UpstreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/api/frame":
            raw = json.dumps(
                {
                    "schema": "terrarium.frame.v1",
                    "frame_version": 1,
                    "logical_width": 800,
                    "logical_height": 480,
                    "tick": 42,
                    "creature": {"name": "Moss"},
                },
                separators=(",", ":"),
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path == "/api/health":
            raw = b'{"ok":true,"tick":42,"events":42}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self.send_error(404)


def _serve(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def test_godot_web_gateway_is_same_origin_read_only_and_fail_closed(tmp_path: Path) -> None:
    web_root = tmp_path / "web"
    web_root.mkdir()
    (web_root / "index.html").write_text("<html>godot</html>", encoding="utf-8")
    (web_root / "index.wasm").write_bytes(b"wasm")

    upstream = ThreadingHTTPServer(("127.0.0.1", 0), _UpstreamHandler)
    upstream_thread = _serve(upstream)
    upstream_url = f"http://127.0.0.1:{upstream.server_address[1]}"

    gateway = GatewayServer(("127.0.0.1", 0), GatewayHandler, web_root=web_root, upstream=upstream_url)
    gateway_thread = _serve(gateway)
    gateway_url = f"http://127.0.0.1:{gateway.server_address[1]}"

    try:
        with urlopen(gateway_url + "/", timeout=2) as response:
            assert response.status == 200
            assert response.read() == b"<html>godot</html>"

        with urlopen(gateway_url + "/index.wasm", timeout=2) as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/wasm"
            assert response.read() == b"wasm"

        with urlopen(gateway_url + "/api/frame", timeout=2) as response:
            payload = json.loads(response.read())
            assert payload["schema"] == "terrarium.frame.v1"
            assert payload["tick"] == 42
            assert response.headers["Cache-Control"] == "no-store"

        request = Request(gateway_url + "/api/frame", data=b"{}", method="POST")
        try:
            urlopen(request, timeout=2)
        except HTTPError as exc:
            assert exc.code == 405
        else:
            raise AssertionError("presentation gateway unexpectedly accepted POST")

        try:
            urlopen(gateway_url + "/api/events", timeout=2)
        except HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("presentation gateway exposed an undeclared API endpoint")

        upstream.shutdown()
        upstream.server_close()
        upstream_thread.join(timeout=2)

        try:
            urlopen(gateway_url + "/", timeout=2)
        except HTTPError as exc:
            assert exc.code == 503
        else:
            raise AssertionError("gateway served an authoritative-looking entry page without canonical frame authority")
    finally:
        gateway.shutdown()
        gateway.server_close()
        gateway_thread.join(timeout=2)
        if upstream_thread.is_alive():
            upstream.shutdown()
            upstream.server_close()
            upstream_thread.join(timeout=2)
