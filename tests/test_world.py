from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from terrarium.engine import WorldEngine
from terrarium.events import verify_chain
from terrarium.frame import make_frame
from terrarium.models import canonical_json
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"


def engine_at(path: Path, seed: int = 1701) -> tuple[WorldStore, WorldEngine]:
    store=WorldStore(path); store.initialize(seed, created_at=FIXED); return store,WorldEngine(store,seed=seed,snapshot_every=10)


def test_deterministic_seed_and_initial_state(tmp_path):
    a_store,a=engine_at(tmp_path/'a'); b_store,b=engine_at(tmp_path/'b')
    a.run_steps(120); b.run_steps(120)
    assert canonical_json(a.current_state()) == canonical_json(b.current_state())
    assert [e['type'] for e in a_store.iter_events()] == [e['type'] for e in b_store.iter_events()]
    a_store.close(); b_store.close()


def test_snapshot_plus_events_reconstructs_exact_state(tmp_path):
    store,engine=engine_at(tmp_path); engine.run_steps(47)
    result=assert_exact_replay(store)
    assert result['ok']; assert result['replayed_state_hash']==result['canonical_state_hash']
    store.close()


def test_restart_preserves_canonical_state_and_object_positions(tmp_path):
    store,engine=engine_at(tmp_path)
    for _ in range(300):
        event=engine.step()
        if event['type']=='object_placed' and sum(int(o['times_moved']) for o in engine.current_state()['objects']) >= 2:
            break
    before=engine.current_state(); store.close()
    reopened=WorldStore(tmp_path); engine2=WorldEngine(reopened,seed=999)
    assert canonical_json(before)==canonical_json(engine2.current_state())
    assert [(o['id'],o['zone'],o['x'],o['y'],o['times_moved']) for o in before['objects']] == [(o['id'],o['zone'],o['x'],o['y'],o['times_moved']) for o in engine2.current_state()['objects']]
    reopened.close()


def test_events_are_ordered_hashed_jsonl_and_sqlite_append_only(tmp_path):
    store,engine=engine_at(tmp_path); engine.run_steps(25)
    events=list(store.iter_events()); verify_chain(events)
    assert [e['seq'] for e in events] == list(range(1,26))
    lines=[json.loads(x) for x in store.log_path.read_text().splitlines() if x]
    assert [e['content_hash'] for e in lines] == [e['content_hash'] for e in events]
    with pytest.raises(sqlite3.DatabaseError): store.conn.execute("DELETE FROM events WHERE seq=1")
    store.close()


def test_world_is_autonomous_and_habitat_accumulates(tmp_path):
    store,engine=engine_at(tmp_path); events=engine.run_steps(240)
    actions={e['details']['action'] for e in events}
    assert len(actions)>=8
    assert sum(e['type']=='object_placed' for e in events)>=4
    assert sum(o['times_moved']>0 for o in engine.current_state()['objects'])>=3
    assert len(engine.current_state()['habitat']['marks'])>=3
    store.close()


def test_frame_contract_is_exact_and_renderer_not_canonical(tmp_path):
    store,engine=engine_at(tmp_path); engine.run_steps(3)
    frame=make_frame(engine.current_state(),last_event=store.last_event())
    assert (frame['logical_width'],frame['logical_height'])==(800,480)
    assert 'rng_state' not in frame and 'energy' not in frame['creature']
    html=(Path('display/web/index.html')).read_text(); js=Path('display/web/app.js').read_text()
    assert 'width="800" height="480"' in html
    assert 'localStorage' not in js and 'sessionStorage' not in js
    store.close()


def test_snapshot_tool_direct_entrypoint(tmp_path):
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "tools/capture_dev_snapshot.py", "pytest-smoke", "--note", "pytest smoke", "--steps", "4"],
        cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    snapshot_dir = Path(__file__).resolve().parents[1] / payload["directory"]
    assert (snapshot_dir / "frame.json").is_file()
    assert (snapshot_dir / "meta.json").is_file()
    # Tests must not leave fake development milestones behind.
    import shutil
    shutil.rmtree(snapshot_dir)
    index = Path(__file__).resolve().parents[1] / "snapshots/index.json"
    data = json.loads(index.read_text())
    data["snapshots"] = [x for x in data["snapshots"] if x["snapshot_id"] != payload["snapshot_id"]]
    index.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
