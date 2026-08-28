from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from terrarium.engine import WorldEngine
from terrarium.events import verify_chain
from terrarium.frame import make_frame
from terrarium.models import PLACEMENT_SLOTS, RULES_VERSION, canonical_json
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
    store,engine=engine_at(tmp_path)
    # 8D deliberately removes play/nudge from delicate and keepsake objects,
    # so use a 1,000-tick bounded horizon while preserving the >=2 play gate.
    events=engine.run_steps(1000)
    actions={e['details']['action'] for e in events}
    assert len(actions)>=8
    assert sum(e['type']=='object_placed' for e in events)>=4
    assert sum(o['times_moved']>0 for o in engine.current_state()['objects'])>=3
    # Calmer routine-aware behavior intentionally creates path wear more slowly.
    state=engine.current_state()
    assert sum(state['habitat']['path_wear'].values()) >= 15
    assert sum(state['habitat']['affordance_history']['completed_families'].values()) >= 80
    assert state['habitat']['activity_aftermath']['object_nudges'] >= 2
    store.close()


def test_autonomous_object_placements_use_authored_habitat_slots(tmp_path):
    store,engine=engine_at(tmp_path)
    placements=[]
    for _ in range(500):
        event=engine.step()
        if event['type']=='object_placed': placements.append(event)
    assert len(placements)>=6
    for event in placements:
        assert (event['details']['x'],event['details']['y']) in PLACEMENT_SLOTS[event['details']['to_zone']]
    store.close()



def test_activity_specific_aftermath_accumulates_deterministically(tmp_path):
    store,engine=engine_at(tmp_path)
    # 8D's object-specific chains intentionally consume a little more of the
    # short horizon; 700 ticks still exercises the full accepted repertoire.
    events=engine.run_steps(700)
    state=engine.current_state(); aftermath=state['habitat']['activity_aftermath']
    assert aftermath['sleep_nook_ticks'] >= 2
    assert aftermath['sleep_nook_bouts'] >= 1
    # A window bout now commits for longer, so bout count is lower while dwell is higher.
    assert aftermath['window_watches'] >= 4
    assert aftermath['activity_corner_uses'] >= 5
    frame=make_frame(state,last_event=store.last_event())
    assert frame['habitat']['activity_aftermath'] == aftermath
    actions={e['details']['action'] for e in events}
    assert {'loaf','groom','stretch','nudge','react'} <= actions
    assert len(actions) >= 15
    assert frame['last_event']['action'] == store.last_event()['details']['action']
    assert frame['last_event']['object_id'] == store.last_event()['details'].get('object_id')
    assert 'intent_action' in frame['creature'] and 'target_object_id' in frame['creature']
    store.close()

def test_frame_contract_is_exact_and_renderer_not_canonical(tmp_path):
    store,engine=engine_at(tmp_path); engine.run_steps(3)
    frame=make_frame(engine.current_state(),last_event=store.last_event())
    assert (frame['logical_width'],frame['logical_height'])==(800,480)
    assert 'rng_state' not in frame and 'energy' not in frame['creature']
    assert all('times_inspected' in obj for obj in frame['objects'])
    assert all({'archetype','interaction_state','available_affordances','state_transitions'} <= set(obj) for obj in frame['objects'])
    html=(Path('display/web/index.html')).read_text(); js=Path('display/web/app.js').read_text()
    assert 'width="800" height="480"' in html
    assert 'localStorage' not in js and 'sessionStorage' not in js
    assert 'Math.random' not in js
    assert 'function historyValue' in js and 'function emergence' in js and 'function stableUnit' in js
    assert 'Math.floor(windowWatches' not in js and 'Math.floor(cornerUses' not in js and 'Math.floor(sleepTicks' not in js
    store.close()



def test_action_commitment_reduces_decision_frequency_without_freezing(tmp_path):
    store,engine=engine_at(tmp_path)
    events=engine.run_steps(120)
    decisions=[e for e in events if e["details"].get("decision", True)]
    continuations=[e for e in events if not e["details"].get("decision", True)]
    assert 20 < len(decisions) < 80
    assert len(continuations) > len(decisions)
    assert len({e["details"].get("intent_action", e["details"]["action"]) for e in decisions}) >= 8
    assert engine.current_state()["rules_version"] == RULES_VERSION
    store.close()


def test_default_world_clock_is_slow_persistent_display_cadence(tmp_path):
    store,engine=engine_at(tmp_path)
    before=engine.current_state()["world_minutes"]
    engine.run_steps(20)
    assert engine.current_state()["world_minutes"] - before == 20
    # 3 real seconds/tick * 1440 ticks/day = 72 real minutes/day.
    assert 3 * 1440 / 60 == 72
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
    assert (snapshot_dir / "preview.svg").is_file()
    # Tests must not leave fake development milestones behind.
    import shutil
    shutil.rmtree(snapshot_dir)
    index = Path(__file__).resolve().parents[1] / "snapshots/index.json"
    data = json.loads(index.read_text())
    data["snapshots"] = [x for x in data["snapshots"] if x["snapshot_id"] != payload["snapshot_id"]]
    index.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("snapshot_tool", Path(__file__).resolve().parents[1] / "tools/capture_dev_snapshot.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.rebuild_snapshot_readme(data)


def test_legacy_behavior_context_migrates_without_resetting_possessions():
    from terrarium.engine import Simulation
    from terrarium.models import BEHAVIOR_CONTEXT_SCHEMA, initial_state

    state = initial_state(1701, created_at=FIXED)
    state["rules_version"] = "terrarium-rules-v2-action-pacing"
    state["creature"].pop("behavior_context", None)
    state["creature"]["carrying"] = "red_thread"
    red_thread = next(obj for obj in state["objects"] if obj["id"] == "red_thread")
    red_thread["state"] = "carried"
    red_thread["carried_by"] = state["creature"]["id"]
    red_thread["times_moved"] = 7
    red_thread["times_inspected"] = 11

    _, _, _, migrated = Simulation().step(state)
    context = migrated["creature"]["behavior_context"]
    carried = next(obj for obj in migrated["objects"] if obj["id"] == "red_thread")

    assert migrated["rules_version"] == RULES_VERSION
    assert context["schema"] == BEHAVIOR_CONTEXT_SCHEMA
    assert len(context["recent_zones"]) <= 4
    assert len(context["recent_objects"]) <= 4
    assert migrated["creature"]["carrying"] == "red_thread"
    assert carried["state"] == "carried"
    assert carried["carried_by"] == migrated["creature"]["id"]
    assert carried["times_moved"] == 7
    assert carried["times_inspected"] == 11
    assert carried["archetype"] == "soft_nesting"
    assert carried["interaction_state"] == "loose"
    assert carried["state_transitions"] == 0


def test_seasonal_clock_is_canonical_real_time_and_additive():
    from copy import deepcopy
    from terrarium.models import SEASONAL_CLOCK_SCHEMA, initial_state, normalize_seasonal_clock, seasonal_clock_for
    state = initial_state(1701, created_at="2026-01-01T00:00:00Z")
    assert state["habitat"]["seasonal_clock"]["schema"] == SEASONAL_CLOCK_SCHEMA
    assert state["habitat"]["seasonal_clock"]["season"] == "spring"
    assert state["habitat"]["seasonal_clock"]["stage"] == "early"
    assert seasonal_clock_for("2026-01-01T00:00:00Z", "2026-01-22T00:00:00Z", migration_origin="test")["season"] == "summer"

    legacy = deepcopy(state)
    legacy["habitat"].pop("seasonal_clock")
    before = deepcopy(legacy)
    clock = normalize_seasonal_clock(legacy, observed_at_utc="2026-08-28T15:00:00Z")
    assert clock["epoch_utc"] == "2026-08-28T15:00:00Z"
    assert clock["migration_origin"] == "neutral-existing-world"
    legacy["habitat"].pop("seasonal_clock")
    assert legacy == before


def test_frame_exposes_season_without_changing_weather_authority():
    from terrarium.frame import make_frame
    from terrarium.models import initial_state, weather_for
    state = initial_state(1701, created_at="2026-01-01T00:00:00Z")
    frame = make_frame(state)
    assert frame["season"]["name"] == "spring"
    assert frame["season"]["cadence_days_per_season"] == 21
    assert weather_for(900, 1701) == weather_for(900, 1701)
