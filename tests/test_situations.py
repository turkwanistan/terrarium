from __future__ import annotations

from copy import deepcopy

from terrarium.engine import Simulation, WorldEngine
from terrarium.models import initial_state
from terrarium.replay import assert_exact_replay
from terrarium.situations import EVENT_CATALOG, SITUATIONAL_EVENTS_SCHEMA, ensure_situational_events
from terrarium.spatial import point_is_walkable
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"


def test_iteration6_world_gets_neutral_additive_situational_event_migration():
    state = initial_state(1701, created_at=FIXED)
    state["habitat"].pop("situational_events")
    before = deepcopy(state)
    events = ensure_situational_events(state)
    assert events["schema"] == SITUATIONAL_EVENTS_SCHEMA
    assert events["migration_origin"] == "neutral-existing-world"
    assert events["active"] is None and events["recent"] == []
    assert all(events["started_counts"][name] == 0 for name in EVENT_CATALOG)
    migrated = deepcopy(state); migrated["habitat"].pop("situational_events")
    assert migrated == before


def test_situational_event_stream_is_deterministic_and_catalog_reachable():
    def run():
        state = initial_state(1701, created_at=FIXED)
        sim = Simulation(); starts = []
        for _ in range(10080):
            _, _, details, state = sim.step(state)
            if details.get("world_event_started"):
                starts.append(details["world_event_started"])
        return state, starts
    a_state, a = run(); b_state, b = run()
    assert a == b and a_state == b_state
    assert set(item["type"] for item in a) == set(EVENT_CATALOG)
    assert 40 <= len(a) <= 90


def test_active_world_event_survives_restart_and_replay(tmp_path):
    store = WorldStore(tmp_path); store.initialize(1701, created_at=FIXED)
    engine = WorldEngine(store, seed=1701, snapshot_every=10)
    for _ in range(400):
        engine.step()
        if engine.current_state()["habitat"]["situational_events"]["active"]:
            break
    before = engine.current_state()
    assert before["habitat"]["situational_events"]["active"] is not None
    assert assert_exact_replay(store)["ok"]
    store.close()
    reopened = WorldStore(tmp_path); engine2 = WorldEngine(reopened, seed=999999)
    assert engine2.current_state() == before
    reopened.close()


def test_sunlight_is_used_only_as_active_walkable_authoritative_affordance():
    state = initial_state(1701, created_at=FIXED); sim = Simulation(); uses = 0
    for _ in range(4000):
        _, _, details, state = sim.step(state)
        if details.get("supported_action") != "sunlight_affordance":
            continue
        uses += 1
        active = state["habitat"]["situational_events"]["active"]
        assert active and active["type"] == "sunlight"
        assert (state["creature"]["x"], state["creature"]["y"]) == (active["x"], active["y"])
        assert point_is_walkable((active["x"], active["y"]))
    assert uses >= 1
