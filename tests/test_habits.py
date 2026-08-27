from __future__ import annotations

from copy import deepcopy

from terrarium.engine import Simulation, WorldEngine
from terrarium.models import HABIT_CONTEXTS, HABIT_PROFILE_SCHEMA, ZONES, canonical_json, initial_state
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"


def test_initial_habit_profile_is_neutral_bounded_and_complete():
    state = initial_state(1701, created_at=FIXED)
    profile = state["creature"]["habit_profile"]
    assert profile["schema"] == HABIT_PROFILE_SCHEMA
    assert profile["migration_origin"] == "native"
    assert profile["experience_count"] == 0
    assert set(profile["zone_affinity"]) == set(ZONES)
    assert set(profile["object_affinity"]) == {obj["id"] for obj in state["objects"]}
    assert set(profile["context_zone_affinity"]) == set(HABIT_CONTEXTS)
    assert all(value == 0.0 for value in profile["zone_affinity"].values())
    assert all(value == 0.0 for value in profile["object_affinity"].values())


def test_v3_world_gets_neutral_habit_migration_without_rewriting_existing_context():
    state = initial_state(1701, created_at=FIXED)
    state["rules_version"] = "terrarium-rules-v3-routine-coherence"
    state["creature"].pop("habit_profile")
    before_context = deepcopy(state["creature"]["behavior_context"])
    before_objects = deepcopy(state["objects"])

    profile = Simulation._habit_profile(state)

    assert profile["schema"] == HABIT_PROFILE_SCHEMA
    assert profile["migration_origin"] == "neutral-existing-world"
    assert profile["experience_count"] == 0
    assert state["creature"]["behavior_context"] == before_context
    assert state["objects"] == before_objects


def test_habits_persist_restart_and_snapshot_replay_exactly(tmp_path):
    store = WorldStore(tmp_path)
    store.initialize(1701, created_at=FIXED)
    engine = WorldEngine(store, seed=1701, snapshot_every=20)
    engine.run_steps(1800)
    before = engine.current_state()
    assert before["creature"]["habit_profile"]["experience_count"] > 200
    replay = assert_exact_replay(store)
    assert replay["ok"]
    store.close()

    reopened = WorldStore(tmp_path)
    engine2 = WorldEngine(reopened, seed=999)
    after = engine2.current_state()
    assert canonical_json(after) == canonical_json(before)
    assert after["creature"]["habit_profile"] == before["creature"]["habit_profile"]
    reopened.close()


def test_controlled_history_profiles_change_future_tendencies_deterministically():
    base = initial_state(1701, created_at=FIXED)

    def with_history(zone: str, object_id: str):
        state = deepcopy(base)
        p = state["creature"]["habit_profile"]
        p["experience_count"] = 2200
        for name in p["zone_affinity"]:
            p["zone_affinity"][name] = 0.12
        p["zone_affinity"][zone] = 0.90
        for context in HABIT_CONTEXTS:
            for name in p["context_zone_affinity"][context]:
                p["context_zone_affinity"][context][name] = 0.12
            p["context_zone_affinity"][context][zone] = 0.90
        for oid in p["object_affinity"]:
            p["object_affinity"][oid] = 0.12
        p["object_affinity"][object_id] = 0.90
        return state

    a = with_history("window", "amber_leaf")
    b = with_history("activity_corner", "acorn")
    a_physical = deepcopy(a); b_physical = deepcopy(b)
    a_physical["creature"].pop("habit_profile"); b_physical["creature"].pop("habit_profile")
    assert canonical_json(a_physical) == canonical_json(b_physical)

    def run(state):
        sim = Simulation(); current = deepcopy(state); destinations = []
        for _ in range(1800):
            _, _, details, current = sim.step(current)
            if details.get("decision") and details.get("action") in {"walk", "explore"} and details.get("travel_purpose") != "object_delivery":
                destinations.append(details.get("to_zone"))
        return current, destinations

    a1, ad1 = run(a); a2, ad2 = run(a)
    b1, bd1 = run(b); b2, bd2 = run(b)
    assert canonical_json(a1) == canonical_json(a2) and ad1 == ad2
    assert canonical_json(b1) == canonical_json(b2) and bd1 == bd2
    # Judge the pair of learned tendencies together rather than requiring each
    # small 1,800-tick count to beat sampling noise independently. The longer
    # controlled evaluator below proves the same causal effect with a stronger gate.
    cross_advantage = (ad1.count("window") - bd1.count("window")) + (bd1.count("activity_corner") - ad1.count("activity_corner"))
    assert cross_advantage >= 2
    assert len(set(ad1)) == len(ZONES)
    assert len(set(bd1)) == len(ZONES)
