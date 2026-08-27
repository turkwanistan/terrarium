from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.migrate_runtime_state import migrate


def _make_legacy(path: Path) -> str:
    path.mkdir(parents=True)
    db = path / "terrarium.sqlite3"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    state = json.dumps({"tick": 42, "creature": {"name": "Moss"}}, sort_keys=True)
    con.execute("INSERT INTO meta(key,value) VALUES('state',?)", (state,))
    con.commit()
    con.close()
    (path / "events.jsonl").write_text('{"seq":1}\n', encoding="utf-8")
    return state


def test_runtime_state_migration_preserves_canonical_state(tmp_path):
    source = tmp_path / "repo-data-live"
    destination = tmp_path / "user-state"
    expected = _make_legacy(source)

    result = migrate(source, destination)
    assert result["migrated"] is True
    con = sqlite3.connect(destination / "terrarium.sqlite3")
    try:
        actual = con.execute("SELECT value FROM meta WHERE key='state'").fetchone()[0]
    finally:
        con.close()
    assert actual == expected
    assert (destination / "events.jsonl").read_text(encoding="utf-8") == '{"seq":1}\n'

    second = migrate(source, destination)
    assert second["migrated"] is False
    assert second["reason"] == "destination already initialized"


def test_launchers_use_user_owned_runtime_state():
    for name in ("scripts/run_lan.sh", "scripts/run_local.sh"):
        text = Path(name).read_text(encoding="utf-8")
        assert "XDG_STATE_HOME" in text
        assert "tools/migrate_runtime_state.py" in text
        assert '--data-dir "$data_dir"' in text
        assert '--tick-seconds 3' in text
