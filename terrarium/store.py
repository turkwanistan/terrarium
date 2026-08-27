from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .events import event_line, verify_event
from .models import canonical_json, initial_state, sha256_json, utc_now


class WorldStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "terrarium.sqlite3"
        self.log_path = self.root / "events.jsonl"
        self.conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self._create_schema()
        self._sync_jsonl_from_db()

    def close(self) -> None:
        self.conn.close()

    def _create_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              seq INTEGER PRIMARY KEY,
              event_id TEXT NOT NULL UNIQUE,
              tick INTEGER NOT NULL,
              event_type TEXT NOT NULL,
              timestamp TEXT NOT NULL,
              schema_version INTEGER NOT NULL,
              event_json TEXT NOT NULL,
              content_hash TEXT NOT NULL UNIQUE,
              prev_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshots (
              snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
              seq INTEGER NOT NULL,
              tick INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              state_json TEXT NOT NULL,
              state_hash TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS events_no_update
              BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete
              BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS snapshots_no_update
              BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT, 'snapshots are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS snapshots_no_delete
              BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT, 'snapshots are immutable'); END;
            """
        )

    def initialize(self, seed: int, *, created_at: str | None = None) -> dict[str, Any]:
        state = self.load_state()
        if state is not None:
            return state
        state = initial_state(seed, created_at=created_at)
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute("INSERT INTO meta(key,value) VALUES('state',?)", (canonical_json(state),))
            self.conn.execute("INSERT INTO meta(key,value) VALUES('seed',?)", (str(seed),))
            self.conn.execute(
                "INSERT INTO snapshots(seq,tick,created_at,state_json,state_hash) VALUES(0,0,?,?,?)",
                (utc_now(), canonical_json(state), sha256_json(state)),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return state

    def load_state(self) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT value FROM meta WHERE key='state'").fetchone()
        return json.loads(row[0]) if row else None

    def event_count(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])

    def last_event(self) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT event_json FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else None

    def append_event(self, event: dict[str, Any], *, state_after: dict[str, Any], snapshot_every: int = 20) -> None:
        verify_event(event)
        last = self.last_event()
        expected_seq = int(last["seq"]) + 1 if last else 1
        expected_hash = str(last["content_hash"]) if last else "0" * 64
        if int(event["seq"]) != expected_seq or event["prev_hash"] != expected_hash:
            raise ValueError("event does not extend canonical ledger")
        state = state_after
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO events(seq,event_id,tick,event_type,timestamp,schema_version,event_json,content_hash,prev_hash) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    int(event["seq"]), event["event_id"], int(event["tick"]), event["type"], event["timestamp"],
                    int(event["event_version"]), canonical_json(event), event["content_hash"], event["prev_hash"],
                ),
            )
            self.conn.execute(
                "INSERT INTO meta(key,value) VALUES('state',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (canonical_json(state),),
            )
            if int(event["seq"]) % snapshot_every == 0:
                self.conn.execute(
                    "INSERT INTO snapshots(seq,tick,created_at,state_json,state_hash) VALUES(?,?,?,?,?)",
                    (int(event["seq"]), int(event["tick"]), utc_now(), canonical_json(state), sha256_json(state)),
                )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        self._append_jsonl(event)

    def _append_jsonl(self, event: dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(event_line(event))
            handle.flush()
            os.fsync(handle.fileno())

    def _sync_jsonl_from_db(self) -> None:
        logged: list[dict[str, Any]] = []
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as handle:
                for n, line in enumerate(handle, 1):
                    if line.strip():
                        try:
                            logged.append(json.loads(line))
                        except json.JSONDecodeError as exc:
                            raise RuntimeError(f"corrupt JSONL event at line {n}") from exc
        rows = [json.loads(r[0]) for r in self.conn.execute("SELECT event_json FROM events ORDER BY seq")]
        if len(logged) > len(rows):
            raise RuntimeError("JSONL ledger is ahead of canonical SQLite ledger")
        for i, event in enumerate(logged):
            if canonical_json(event) != canonical_json(rows[i]):
                raise RuntimeError(f"JSONL ledger diverges at event {i + 1}")
        for event in rows[len(logged):]:
            self._append_jsonl(event)

    def iter_events(self, *, after_seq: int = 0, through_seq: int | None = None) -> Iterable[dict[str, Any]]:
        sql = "SELECT event_json FROM events WHERE seq > ?"
        args: list[Any] = [after_seq]
        if through_seq is not None:
            sql += " AND seq <= ?"
            args.append(through_seq)
        sql += " ORDER BY seq"
        for row in self.conn.execute(sql, args):
            yield json.loads(row[0])

    def latest_snapshot(self, *, through_seq: int | None = None) -> dict[str, Any]:
        if through_seq is None:
            row = self.conn.execute("SELECT * FROM snapshots ORDER BY seq DESC, snapshot_id DESC LIMIT 1").fetchone()
        else:
            row = self.conn.execute(
                "SELECT * FROM snapshots WHERE seq <= ? ORDER BY seq DESC, snapshot_id DESC LIMIT 1", (through_seq,)
            ).fetchone()
        if row is None:
            raise RuntimeError("no snapshot available")
        return dict(row)
