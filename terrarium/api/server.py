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
ART_ROOT = PROJECT_ROOT / "display" / "art"
SNAPSHOT_ROOT = PROJECT_ROOT / "snapshots"


class TerrariumServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, engine: WorldEngine, *, dev_temporal_fixtures: Path | None = None, dev_temporal_output_dir: Path | None = None):
        super().__init__(address, handler)
        self.engine = engine
        self.dev_temporal_fixtures = dev_temporal_fixtures
        self.dev_temporal_output_dir = dev_temporal_output_dir


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

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/dev/temporal-evidence" or self.server.dev_temporal_output_dir is None:
            self._json({"error": "development temporal evidence sink is disabled"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json({"error": "invalid content length"}, 400)
            return
        if length <= 0 or length > 2_000_000:
            self._json({"error": "temporal evidence payload must be 1..2000000 bytes"}, 413)
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json({"error": "invalid JSON evidence payload"}, 400)
            return
        scenario = str(payload.get("scenario", "capture"))
        mode = str(payload.get("easing", payload.get("schema", "evidence")))
        safe = lambda text: "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in text)[:80] or "evidence"
        output_dir = self.server.dev_temporal_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{safe(scenario)}-{safe(mode)}.json"
        temp = output_path.with_suffix(output_path.suffix + ".tmp")
        temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp.replace(output_path)
        self._json({"ok": True, "path": str(output_path)})

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
        if parsed.path == "/api/dev/temporal-fixtures":
            fixture_path = self.server.dev_temporal_fixtures
            if fixture_path is None:
                self._json({"error": "development temporal fixtures are disabled"}, 404)
                return
            try:
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                self._json({"error": f"unable to load temporal fixtures: {exc}"}, 500)
                return
            self._json(payload)
            return
        if parsed.path == "/api/step":
            self._json({"error": "world-authoritative mutation is not exposed over GET"}, 405)
            return
        if parsed.path == "/snapshots" or parsed.path.startswith("/snapshots/"):
            rel = parsed.path[len("/snapshots"):].lstrip("/")
            self._static_from(SNAPSHOT_ROOT, rel)
            return
        if parsed.path == "/art" or parsed.path.startswith("/art/"):
            rel = parsed.path[len("/art"):].lstrip("/")
            self._static_from(ART_ROOT, rel)
            return
        self._static_from(WEB_ROOT, parsed.path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the persistent Terrarium world and reference renderer.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--data-dir", default=str(PROJECT_ROOT / "data"))
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--tick-seconds", type=float, default=3.0)
    parser.add_argument("--minutes-per-tick", type=int, default=1)
    parser.add_argument("--snapshot-every", type=int, default=20)
    parser.add_argument(
        "--dev-temporal-fixtures",
        default=None,
        help="Development-only JSON fixture pack exposed at /api/dev/temporal-fixtures.",
    )
    parser.add_argument(
        "--dev-temporal-output-dir",
        default=None,
        help="Development-only bounded browser evidence sink directory.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = WorldStore(args.data_dir)
    engine = WorldEngine(
        store,
        seed=args.seed,
        minutes_per_tick=args.minutes_per_tick,
        snapshot_every=args.snapshot_every,
        real_time_seasons=True,
    )
    engine.start(tick_seconds=args.tick_seconds)
    fixture_path = Path(args.dev_temporal_fixtures).resolve() if args.dev_temporal_fixtures else None
    output_dir = Path(args.dev_temporal_output_dir).resolve() if args.dev_temporal_output_dir else None
    server = TerrariumServer(
        (args.host, args.port),
        Handler,
        engine,
        dev_temporal_fixtures=fixture_path,
        dev_temporal_output_dir=output_dir,
    )
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
