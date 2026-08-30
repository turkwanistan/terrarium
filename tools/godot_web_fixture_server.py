from __future__ import annotations

import argparse
import json
import mimetypes
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB_ROOT = ROOT / "display" / "web" / "godot"
DEFAULT_FIXTURES = ROOT / "artifacts" / "godot-art-gate" / "web-deep-debug" / "fixtures.json"
EXPLICIT_MIME_TYPES = {
    ".wasm": "application/wasm",
    ".pck": "application/octet-stream",
    ".js": "text/javascript; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".png": "image/png",
}


class FixtureState:
    def __init__(self, frames: list[dict]):
        if not frames:
            raise ValueError("fixture sequence must contain at least one frame")
        self._frames = frames
        self._next_index = 0
        self._requests = 0
        self._lock = threading.Lock()

    def next_frame(self) -> tuple[int, dict]:
        with self._lock:
            index = min(self._next_index, len(self._frames) - 1)
            frame = self._frames[index]
            if self._next_index < len(self._frames) - 1:
                self._next_index += 1
            self._requests += 1
            return index, frame

    def status(self) -> dict:
        with self._lock:
            return {
                "schema": "terrarium.godot-web-fixture-status.v1",
                "requests": self._requests,
                "next_index": self._next_index,
                "frame_count": len(self._frames),
                "complete": self._next_index >= len(self._frames) - 1,
                "last_tick": int(self._frames[-1].get("tick", -1)),
            }


class FixtureServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, *, web_root: Path, state: FixtureState):
        super().__init__(address, handler)
        self.web_root = web_root.resolve()
        self.state = state


class FixtureHandler(BaseHTTPRequestHandler):
    server: FixtureServer
    server_version = "TerrariumGodotWebFixture/1"

    def log_message(self, format: str, *args) -> None:
        return

    def _send_bytes(
        self,
        raw: bytes,
        *,
        status: int = 200,
        content_type: str = "application/octet-stream",
        headers: dict[str, str] | None = None,
        head_only: bool = False,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if headers:
            for name, value in headers.items():
                self.send_header(name, value)
        self.end_headers()
        if not head_only:
            self.wfile.write(raw)

    def _json(self, payload: dict, *, status: int = 200, headers: dict[str, str] | None = None, head_only: bool = False) -> None:
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._send_bytes(
            raw,
            status=status,
            content_type="application/json; charset=utf-8",
            headers=headers,
            head_only=head_only,
        )

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

    def _handle_read(self, *, head_only: bool = False) -> None:
        path = urlparse(self.path).path
        if path == "/api/frame":
            index, frame = self.server.state.next_frame()
            self._json(frame, headers={"X-Terrarium-Fixture-Index": str(index)}, head_only=head_only)
            return
        if path == "/api/health":
            status = self.server.state.status()
            self._json({"ok": True, **status}, head_only=head_only)
            return
        if path == "/fixture/status":
            self._json(self.server.state.status(), head_only=head_only)
            return
        static_path = self._static_path(path)
        if static_path is None:
            self._json({"error": "fixture resource not found"}, status=HTTPStatus.NOT_FOUND, head_only=head_only)
            return
        suffix = static_path.suffix.lower()
        content_type = EXPLICIT_MIME_TYPES.get(suffix) or mimetypes.guess_type(static_path.name)[0] or "application/octet-stream"
        self._send_bytes(static_path.read_bytes(), content_type=content_type, head_only=head_only)

    def do_GET(self) -> None:
        self._handle_read()

    def do_HEAD(self) -> None:
        self._handle_read(head_only=True)

    def _reject_write(self) -> None:
        self._json({"error": "fixture server is read-only"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    def do_POST(self) -> None:
        self._reject_write()

    def do_PUT(self) -> None:
        self._reject_write()

    def do_PATCH(self) -> None:
        self._reject_write()

    def do_DELETE(self) -> None:
        self._reject_write()


def load_frames(path: Path, sequence: str) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "terrarium.godot-web-debug-fixtures.v1":
        raise ValueError(f"unexpected fixture schema: {payload.get('schema')}")
    frames = payload.get("sequences", {}).get(sequence)
    if not isinstance(frames, list) or not frames:
        raise ValueError(f"fixture sequence not found: {sequence}")
    return frames


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the actual Godot Web export against an isolated deterministic frame sequence.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8876)
    parser.add_argument("--web-root", type=Path, default=DEFAULT_WEB_ROOT)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--sequence", default="composite")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    web_root = args.web_root.resolve()
    if not (web_root / "index.html").is_file():
        raise SystemExit(f"Godot web build missing: {web_root / 'index.html'}")
    frames = load_frames(args.fixtures.resolve(), args.sequence)
    server = FixtureServer((args.host, args.port), FixtureHandler, web_root=web_root, state=FixtureState(frames))
    print(f"Terrarium Godot Web fixture: http://{args.host}:{server.server_address[1]}/?terrarium_debug=1&terrarium_poll_ms=300", flush=True)
    try:
        server.serve_forever(poll_interval=0.05)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
