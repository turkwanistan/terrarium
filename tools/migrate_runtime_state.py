#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path


def _state_value(db_path: Path) -> str | None:
    if not db_path.is_file():
        return None
    uri = f"file:{db_path.resolve()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        row = con.execute("SELECT value FROM meta WHERE key='state'").fetchone()
        return None if row is None else str(row[0])
    finally:
        con.close()


def migrate(source: Path, destination: Path) -> dict[str, object]:
    source = source.resolve()
    destination = destination.expanduser().resolve()
    src_db = source / "terrarium.sqlite3"
    dst_db = destination / "terrarium.sqlite3"

    destination.mkdir(parents=True, exist_ok=True)
    probe = destination / ".terrarium-write-probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        raise RuntimeError(f"runtime directory is not writable: {destination}: {exc}") from exc

    if dst_db.exists():
        return {"migrated": False, "reason": "destination already initialized", "destination": str(destination)}
    if not src_db.exists():
        return {"migrated": False, "reason": "no legacy state found", "destination": str(destination)}

    src_uri = f"file:{src_db}?mode=ro"
    src = sqlite3.connect(src_uri, uri=True)
    dst = sqlite3.connect(dst_db)
    try:
        src.backup(dst)
        dst.commit()
    finally:
        dst.close()
        src.close()

    src_log = source / "events.jsonl"
    if src_log.is_file():
        shutil.copyfile(src_log, destination / "events.jsonl")

    source_state = _state_value(src_db)
    destination_state = _state_value(dst_db)
    if source_state != destination_state:
        dst_db.unlink(missing_ok=True)
        (destination / "events.jsonl").unlink(missing_ok=True)
        raise RuntimeError("runtime-state migration verification failed: canonical state differs")

    return {
        "migrated": True,
        "source": str(source),
        "destination": str(destination),
        "canonical_state_verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely migrate legacy repo-local Terrarium runtime state.")
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    print(json.dumps(migrate(Path(args.source), Path(args.destination)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
