from __future__ import annotations

import random
from collections import Counter
from copy import deepcopy

from terrarium.engine import Simulation, WorldEngine
from terrarium.models import AFFORDANCE_HISTORY_SCHEMA, HABIT_CONTEXTS, OBJECT_AFFORDANCE_SCHEMA, PLACEMENT_SLOTS, canonical_json, initial_state, object_affordances, weather_for
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"


def _mature_history(state: dict, *, zone: str, object_id: str) -> dict:
    result = deepcopy(state)
    profile = result["creature"]["habit_profile"]
    profile["experience_count"] = 2200
    for name in profile["zone_affinity"]:
        profile["zone_affinity"][name] = 0.12
    profile["zone_affinity"][zone] = 0.90
    for context in HABIT_CONTEXTS:
        for name in profile["context_zone_affinity"][context]:
            profile["context_zone_affinity"][context][name] = 0.12
        profile["context_zone_affinity"][context][zone] = 0.90
    for oid in profile["object_affinity"]:
        profile["object_affinity"][oid] = 0.12
    profile["object_affinity"][object_id] = 0.90
    return result


def test_iteration5_world_gets_neutral_additive_affordance_migration():
    state = initial_state(1701, created_at=FIXED)
    state["rules_version"] = "terrarium-rules-v4-long-horizon-habits"
    state["habitat"].pop("affordance_history", None)
    for obj in state["objects"]:
        obj.pop("times_nudged", None)
    for key in ("loaf_sessions", "groom_sessions", "stretch_sessions", "object_nudges", "arrangement_places", "weather_reactions"):
        state["habitat"]["activity_aftermath"].pop(key, None)
    before_objects = [(o["id"], o["zone"], o["x"], o["y"], o["times_moved"], o["times_inspected"]) for o in state["objects"]]

    history = Simulation._affordance_history(state)

    assert history["schema"] == AFFORDANCE_HISTORY_SCHEMA
    assert history["completed_families"] == {}
    assert history["object_nudges"] == {}
    assert all(value == 0 for value in history["zone_comfort"].values())
    assert all(value == 0 for value in history["zone_arrangements"].values())
    assert history["last_weather_reaction_block"] == -1
    assert all(obj["times_nudged"] == 0 for obj in state["objects"])
    assert before_objects == [(o["id"], o["zone"], o["x"], o["y"], o["times_moved"], o["times_inspected"]) for o in state["objects"]]


def test_nudge_changes_authoritative_object_state_in_authored_slot():
    state = initial_state(1701, created_at=FIXED)
    sim = Simulation()
    found = None
    for _ in range(800):
        before = deepcopy(state)
        _, _, details, state = sim.step(state)
        if details.get("decision") and details.get("action") == "nudge":
            found = (before, details, state)
            break
    assert found is not None
    before, details, after = found
    oid = details["object_id"]
    old = next(obj for obj in before["objects"] if obj["id"] == oid)
    new = next(obj for obj in after["objects"] if obj["id"] == oid)
    assert (details["target_x"], details["target_y"]) == (old["x"], old["y"])
    assert (details["result_x"], details["result_y"]) == (new["x"], new["y"])
    assert (new["x"], new["y"]) != (old["x"], old["y"])
    assert (new["x"], new["y"]) in PLACEMENT_SLOTS[new["zone"]]
    assert new["times_nudged"] == old.get("times_nudged", 0) + 1
    assert new["times_moved"] == old["times_moved"] + 1
    assert after["habitat"]["activity_aftermath"]["object_nudges"] >= 1


def test_object_specific_play_chains_roll_retrieve_and_tug_nest():
    state = initial_state(1701, created_at=FIXED)
    sim = Simulation(); decisions = []
    for _ in range(3200):
        _, _, details, state = sim.step(state)
        if details.get("decision"):
            decisions.append(details)

    rolls = [(i, row) for i, row in enumerate(decisions) if row.get("object_affordance") == "roll"]
    assert len(rolls) >= 3
    recovered = sum(
        any(candidate.get("object_id") == row.get("object_id") and candidate.get("object_affordance") == "retrieve"
            for candidate in decisions[i + 1:i + 3])
        for i, row in rolls
    )
    assert recovered / len(rolls) >= 0.90

    tugs = [(i, row) for i, row in enumerate(decisions) if row.get("object_affordance") == "tug"]
    assert tugs
    nested = sum(
        any(candidate.get("object_id") == row.get("object_id") and candidate.get("object_affordance") == "nest"
            for candidate in decisions[i + 1:i + 3])
        for i, row in tugs
    )
    # Genuine exhaustion may still interrupt an unlocked nesting opportunity;
    # the long-run 8D evaluator uses the same bounded causal threshold.
    assert nested / len(tugs) >= 0.75
    assert all(row.get("object_archetype") in {"rolling", "soft_nesting"} for row in decisions if row.get("action") == "nudge")


def test_object_archetypes_expose_materially_different_stateful_affordances():
    state = initial_state(1701, created_at=FIXED)
    objects = {obj["id"]: obj for obj in state["objects"]}
    assert objects["blue_stone"]["affordance_schema"] == OBJECT_AFFORDANCE_SCHEMA
    assert set(object_affordances(objects["blue_stone"])) == {"inspect", "carry", "nudge"}
    assert set(object_affordances(objects["amber_leaf"])) == {"inspect", "carry"}
    assert set(object_affordances(objects["shell"])) == {"inspect", "carry"}
    assert set(object_affordances(objects["red_thread"])) == {"inspect", "carry", "nudge"}

    objects["blue_stone"]["interaction_state"] = "rolled"
    assert set(object_affordances(objects["blue_stone"])) == {"inspect", "carry"}
    objects["red_thread"]["interaction_state"] = "rumpled"
    assert set(object_affordances(objects["red_thread"])) == {"inspect", "carry", "nest"}
    objects["red_thread"]["interaction_state"] = "nested"
    assert set(object_affordances(objects["red_thread"])) == {"inspect", "carry"}


def test_weather_stream_is_deterministic_calm_and_non_degenerate():
    a = [weather_for(block * 180, 1701) for block in range(60)]
    b = [weather_for(block * 180, 1701) for block in range(60)]
    assert a == b
    counts = Counter(a)
    assert set(counts) == {"clear", "rain", "mist"}
    assert counts["clear"] > counts["rain"] > 0
    assert counts["clear"] > counts["mist"] > 0


def test_learned_zone_history_shapes_arrangement_destination_without_lock_in():
    base = initial_state(1701, created_at=FIXED)
    window = _mature_history(base, zone="window", object_id="amber_leaf")
    activity = _mature_history(base, zone="activity_corner", object_id="amber_leaf")
    sim = Simulation()

    def sample(state: dict) -> Counter[str]:
        counts: Counter[str] = Counter()
        for seed in range(1200):
            counts[sim._choose_arrangement_destination(
                random.Random(seed), state, zone="open_space", object_id="amber_leaf",
                habit_profile=state["creature"]["habit_profile"],
            )] += 1
        return counts

    a = sample(window); b = sample(activity)
    assert a["window"] > b["window"]
    assert b["activity_corner"] > a["activity_corner"]
    assert max(a.values()) / sum(a.values()) < 0.70
    assert max(b.values()) / sum(b.values()) < 0.70


def test_affordance_history_persists_restart_and_replay(tmp_path):
    store = WorldStore(tmp_path); store.initialize(1701, created_at=FIXED)
    engine = WorldEngine(store, seed=1701, snapshot_every=20)
    engine.run_steps(500)
    before = engine.current_state()
    assert before["habitat"]["activity_aftermath"]["object_nudges"] > 0
    assert before["habitat"]["affordance_history"]["completed_families"].get("play", 0) > 0
    assert sum(int(obj.get("state_transitions", 0)) for obj in before["objects"]) > 0
    assert all(obj.get("affordance_schema") == OBJECT_AFFORDANCE_SCHEMA for obj in before["objects"])
    replay = assert_exact_replay(store)
    assert replay["ok"]
    store.close()

    reopened = WorldStore(tmp_path); engine2 = WorldEngine(reopened, seed=999)
    assert canonical_json(engine2.current_state()) == canonical_json(before)
    reopened.close()
