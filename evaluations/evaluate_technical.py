#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import WorldEngine
from terrarium.events import verify_chain
from terrarium.frame import make_frame
from terrarium.models import FRAME_HEIGHT, FRAME_WIDTH, canonical_json
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore


def evaluate(steps: int = 80) -> dict:
    with tempfile.TemporaryDirectory(prefix="terrarium-tech-") as tmp:
        store = WorldStore(tmp)
        store.initialize(1701, created_at="2026-01-01T00:00:00Z")
        engine = WorldEngine(store, seed=1701, snapshot_every=10)
        engine.run_steps(steps)
        state_before = engine.current_state()
        events = list(store.iter_events())
        chain_tip = verify_chain(events)
        replay = assert_exact_replay(store)
        frame = make_frame(state_before, last_event=store.last_event())
        store.close()

        reopened = WorldStore(tmp)
        engine2 = WorldEngine(reopened, seed=999999)
        restart_same = canonical_json(engine2.current_state()) == canonical_json(state_before)
        jsonl_lines = sum(1 for line in reopened.log_path.read_text().splitlines() if line.strip())
        # SQLite itself enforces append-only event records.
        append_only_enforced = False
        try:
            reopened.conn.execute("UPDATE events SET event_type='tampered' WHERE seq=1")
        except sqlite3.DatabaseError:
            append_only_enforced = True
        current = engine2.current_state()
        payload_bytes = len(json.dumps(make_frame(current)).encode())
        db_bytes = reopened.db_path.stat().st_size
        log_bytes = reopened.log_path.stat().st_size
        checks = {
            "logical_viewport_exact": frame["logical_width"] == FRAME_WIDTH == 800 and frame["logical_height"] == FRAME_HEIGHT == 480,
            "restart_preserves_state": restart_same,
            "event_chain_valid": chain_tip == events[-1]["content_hash"],
            "jsonl_matches_event_count": jsonl_lines == len(events),
            "append_only_sqlite_enforced": append_only_enforced,
            "snapshot_event_replay_exact": replay["ok"],
            "renderer_frame_is_semantic": "energy" not in frame["creature"] and frame["schema"] == "terrarium.frame.v1",
        }
        result = {
            "schema":"terrarium.technical-evaluation.v1",
            "passed":all(checks.values()),
            "checks":checks,
            "metrics":{"events":len(events),"frame_payload_bytes":payload_bytes,"sqlite_bytes":db_bytes,"jsonl_bytes":log_bytes,"replay":replay},
        }
        reopened.close()
        return result


def main() -> int:
    p=argparse.ArgumentParser();p.add_argument("--steps",type=int,default=80);p.add_argument("--out")
    a=p.parse_args(); result=evaluate(a.steps); text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out: Path(a.out).write_text(text)
    print(text,end=""); return 0 if result["passed"] else 2

if __name__ == "__main__": raise SystemExit(main())
