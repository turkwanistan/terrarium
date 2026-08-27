from __future__ import annotations

import argparse
import json
import mimetypes
import signal
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from terrarium.engine import WorldEngine
from terrarium.frame import make_frame
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "display" / "web"
SNAPSHOT_ROOT = PROJECT_ROOT / "snapshots"


class TerrariumServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, engine: WorldEngine):
        super().__init__(address, handler)
        self.engine = engine


class Handler(BaseHTTPRequestHandler):
    server: TerrariumServer

    def log_message(self, format: str, *args) -> None:  # quieter service logs
        return

    def _json(self, payload, status: int = 200) -> None:
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _static_from(self, root: Path, rel: str) -> None:
        rel = "index.html" if rel in {"", "/"} else rel.lstrip("/")
        path = (root / rel).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            state = self.server.engine.current_state()
            self._json({"ok": True, "tick": state["tick"], "events": self.server.engine.store.event_count()})
            return
        if parsed.path == "/api/frame":
            state = self.server.engine.current_state()
            self._json(make_frame(state, last_event=self.server.engine.store.last_event()))
            return
        if parsed.path == "/api/events":
            query = parse_qs(parsed.query)
            limit = min(100, max(1, int(query.get("limit", [20])[0])))
            count = self.server.engine.store.event_count()
            after = max(0, count - limit)
            self._json({"events": list(self.server.engine.store.iter_events(after_seq=after))})
            return
        if parsed.path == "/api/debug":
            state = self.server.engine.current_state()
            self._json(
                {
                    "state": state,
                    "event_count": self.server.engine.store.event_count(),
                    "replay": assert_exact_replay(self.server.engine.store),
                }
            )
            return
        if parsed.path == "/api/step":
            self._json({"error": "world-authoritative mutation is not exposed over GET"}, 405)
            return
        if parsed.path == "/snapshots" or parsed.path.startswith("/snapshots/"):
            rel = parsed.path[len("/snapshots"):].lstrip("/")
            self._static_from(SNAPSHOT_ROOT, rel)
            return
        self._static_from(WEB_ROOT, parsed.path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the persistent Terrarium world and reference renderer.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--data-dir", default=str(PROJECT_ROOT / "data"))
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--tick-seconds", type=float, default=3.0)
    parser.add_argument("--minutes-per-tick", type=int, default=8)
    parser.add_argument("--snapshot-every", type=int, default=20)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = WorldStore(args.data_dir)
    engine = WorldEngine(
        store,
        seed=args.seed,
        minutes_per_tick=args.minutes_per_tick,
        snapshot_every=args.snapshot_every,
    )
    engine.start(tick_seconds=args.tick_seconds)
    server = TerrariumServer((args.host, args.port), Handler, engine)
    stopping = threading.Event()

    def stop(*_):
        if not stopping.is_set():
            stopping.set()
            threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        engine.stop()
        server.server_close()
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
