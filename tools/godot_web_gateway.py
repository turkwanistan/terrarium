from __future__ import annotations

import argparse
import json
import mimetypes
import ssl
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB_ROOT = PROJECT_ROOT / "display" / "web" / "godot"
ALLOWED_API_PATHS = {"/api/frame", "/api/health"}
EXPLICIT_MIME_TYPES = {
    ".wasm": "application/wasm",
    ".pck": "application/octet-stream",
    ".js": "text/javascript; charset=utf-8",
    ".html": "text/html; charset=utf-8",
}


class GatewayServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, *, web_root: Path, upstream: str):
        super().__init__(address, handler)
        self.web_root = web_root.resolve()
        self.upstream = upstream.rstrip("/")


class GatewayHandler(BaseHTTPRequestHandler):
    server: GatewayServer
    server_version = "TerrariumGodotGateway/1"

    def log_message(self, format: str, *args) -> None:
        return

    def _send_bytes(
        self,
        raw: bytes,
        *,
        status: int = 200,
        content_type: str = "application/octet-stream",
        cache_control: str = "no-store",
        head_only: bool = False,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", cache_control)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        if not head_only:
            self.wfile.write(raw)

    def _json_error(self, status: int, message: str, *, head_only: bool = False) -> None:
        raw = json.dumps({"error": message}, separators=(",", ":")).encode("utf-8")
        self._send_bytes(
            raw,
            status=status,
            content_type="application/json; charset=utf-8",
            head_only=head_only,
        )

    def _fetch_upstream(self, path: str) -> tuple[int, str, bytes]:
        request = Request(self.server.upstream + path, method="GET")
        try:
            with urlopen(request, timeout=1.5) as response:
                raw = response.read()
                content_type = response.headers.get("Content-Type", "application/json; charset=utf-8")
                return int(response.status), content_type, raw
        except HTTPError as exc:
            raw = exc.read() if exc.fp is not None else b""
            content_type = exc.headers.get("Content-Type", "application/json; charset=utf-8")
            return int(exc.code), content_type, raw
        except (URLError, TimeoutError, OSError) as exc:
            raise ConnectionError(str(exc)) from exc

    def _upstream_frame_ready(self) -> bool:
        try:
            status, _, raw = self._fetch_upstream("/api/frame")
        except ConnectionError:
            return False
        return status == 200 and b'"schema":"terrarium.frame.v1"' in raw

    def _proxy_api(self, path: str, *, head_only: bool = False) -> None:
        if path not in ALLOWED_API_PATHS:
            self._json_error(HTTPStatus.NOT_FOUND, "read-only presentation endpoint not found", head_only=head_only)
            return
        try:
            status, content_type, raw = self._fetch_upstream(path)
        except ConnectionError:
            self._json_error(HTTPStatus.SERVICE_UNAVAILABLE, "canonical Terrarium API unavailable", head_only=head_only)
            return
        self._send_bytes(raw, status=status, content_type=content_type, head_only=head_only)

    def _static_path(self, request_path: str) -> Path | None:
        rel = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        candidate = (self.server.web_root / rel).resolve()
        try:
            candidate.relative_to(self.server.web_root)
        except ValueError:
            return None
        if candidate.is_dir():
            candidate = (candidate / "index.html").resolve()
        return candidate if candidate.is_file() else None

    def _serve_static(self, request_path: str, *, head_only: bool = False) -> None:
        # The browser build must never come up as an authoritative-looking stale scene
        # when the living world cannot be reached. Gate the entry page on a real frame.
        if request_path in {"", "/", "/index.html"} and not self._upstream_frame_ready():
            self._json_error(HTTPStatus.SERVICE_UNAVAILABLE, "canonical Terrarium frame endpoint unavailable", head_only=head_only)
            return
        path = self._static_path(request_path)
        if path is None:
            self._json_error(HTTPStatus.NOT_FOUND, "presentation asset not found", head_only=head_only)
            return
        suffix = path.suffix.lower()
        content_type = EXPLICIT_MIME_TYPES.get(suffix) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self._send_bytes(
            path.read_bytes(),
            content_type=content_type,
            cache_control="no-cache",
            head_only=head_only,
        )

    def _handle_read(self, *, head_only: bool = False) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._proxy_api(parsed.path, head_only=head_only)
        else:
            self._serve_static(parsed.path, head_only=head_only)

    def do_GET(self) -> None:
        self._handle_read()

    def do_HEAD(self) -> None:
        self._handle_read(head_only=True)

    def do_POST(self) -> None:
        self._json_error(HTTPStatus.METHOD_NOT_ALLOWED, "Godot web gateway is read-only")

    def do_PUT(self) -> None:
        self.do_POST()

    def do_PATCH(self) -> None:
        self.do_POST()

    def do_DELETE(self) -> None:
        self.do_POST()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the read-only Terrarium Godot web presentation over HTTPS.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--upstream", required=True, help="Existing canonical Terrarium API base URL.")
    parser.add_argument("--web-root", type=Path, default=DEFAULT_WEB_ROOT)
    parser.add_argument("--cert", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    web_root = args.web_root.resolve()
    if not (web_root / "index.html").is_file():
        raise SystemExit(f"Godot web build missing: {web_root / 'index.html'}")
    if not args.cert.is_file() or not args.key.is_file():
        raise SystemExit("TLS certificate/key missing")

    server = GatewayServer((args.host, args.port), GatewayHandler, web_root=web_root, upstream=args.upstream)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=args.cert, keyfile=args.key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
