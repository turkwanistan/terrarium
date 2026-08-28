from __future__ import annotations

from copy import deepcopy

from terrarium.consequences import (
    CONSEQUENCE_MEMORY_LIMIT,
    CONSEQUENCE_MEMORY_SCHEMA,
    consequence_opportunities,
    ensure_consequence_memory,
    record_consequence,
)
from terrarium.engine import Simulation, WorldEngine
from terrarium.frame import make_frame
from terrarium.models import canonical_json, initial_state
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"


def test_consequence_memory_migrates_additively_without_fabricated_history():
    state = initial_state(1701, created_at=FIXED)
    state["habitat"].pop("consequence_memory")
    before_objects = deepcopy(state["objects"])
    before_habits = deepcopy(state["creature"]["habit_profile"])

    memory = ensure_consequence_memory(state)

    assert memory["schema"] == CONSEQUENCE_MEMORY_SCHEMA
    assert memory["migration_origin"] == "neutral-existing-world"
    assert memory["entries"] == []
    assert state["objects"] == before_objects
    assert state["creature"]["habit_profile"] == before_habits


def test_consequence_memory_is_bounded_and_compacts_repeated_causes():
    state = initial_state(1701, created_at=FIXED)
    first = record_consequence(
        state,
        kind="object_arrangement",
        zone="open_space",
        object_id="blue_stone",
        source={"cause": "controlled"},
        min_delay_minutes=1,
    )
    second = record_consequence(
        state,
        kind="object_arrangement",
        zone="open_space",
        object_id="blue_stone",
        source={"cause": "controlled-repeat"},
        min_delay_minutes=1,
    )
    assert first["id"] == second["id"]
    assert second["source_count"] == 2

    for index in range(CONSEQUENCE_MEMORY_LIMIT + 12):
        state["tick"] += 1
        state["world_minutes"] += 1
        record_consequence(
            state,
            kind=f"trace_{index}",
            zone="window" if index % 2 else "open_space",
            source={"cause": "boundedness", "index": index},
            min_delay_minutes=1,
        )
    assert len(state["habitat"]["consequence_memory"]["entries"]) == CONSEQUENCE_MEMORY_LIMIT


def test_equal_visible_worlds_can_have_different_causal_opportunities_deterministically():
    with_history = initial_state(1701, created_at=FIXED)
    without_history = deepcopy(with_history)
    record_consequence(
        with_history,
        kind="object_arrangement",
        zone="window",
        object_id="amber_leaf",
        strength=1.0,
        source={"cause": "controlled-history"},
        min_delay_minutes=1,
    )
    with_history["world_minutes"] += 2
    without_history["world_minutes"] += 2

    # The renderer sees the same present world. The causal distinction lives in
    # canonical simulation state, not renderer-local memory.
    assert canonical_json(make_frame(with_history)) == canonical_json(make_frame(without_history))
    first = consequence_opportunities(with_history)
    repeat = consequence_opportunities(deepcopy(with_history))
    assert first == repeat
    assert first and first[0]["object_id"] == "amber_leaf"
    assert consequence_opportunities(without_history) == []


def test_existing_intent_machine_executes_bounded_consequence_revisit():
    state = initial_state(1701, created_at=FIXED)
    memory = record_consequence(
        state,
        kind="object_arrangement",
        zone="open_space",
        object_id="blue_stone",
        strength=1.0,
        source={"cause": "controlled-chain"},
        min_delay_minutes=1,
    )
    state["world_minutes"] += 2
    state["creature"]["activity"] = "idle"
    state["creature"]["behavior_commitment"] = {"action": None, "ticks_remaining": 0, "object_id": None}
    state["creature"]["behavior_context"]["intent"] = {
        "kind": "consequence_revisit",
        "stage": "noticed",
        "memory_id": memory["id"],
        "target_zone": "open_space",
        "object_id": "blue_stone",
        "engage_action": "inspect",
    }

    sim = Simulation()
    roles: list[str] = []
    for _ in range(16):
        _, _, details, state = sim.step(state)
        if details.get("consequence_role"):
            roles.append(str(details["consequence_role"]))
        if state["habitat"]["consequence_memory"]["revisit_count"]:
            break

    assert "approach" in roles
    assert "engage" in roles
    assert state["habitat"]["consequence_memory"]["revisit_count"] == 1
    assert state["creature"]["behavior_context"]["intent"]["kind"] == "consequence_recovery"
    assert state["creature"]["carrying"] is None


def test_consequence_state_survives_store_restart_and_exact_replay(tmp_path):
    root = tmp_path / "world"
    store = WorldStore(root)
    engine = WorldEngine(store, seed=1701, snapshot_every=20)
    engine.run_steps(700)
    state = engine.current_state()
    assert state["habitat"]["consequence_memory"]["created_count"] > 0
    before = assert_exact_replay(store)
    store.close()

    reopened = WorldStore(root)
    restarted = WorldEngine(reopened, seed=999)
    after = assert_exact_replay(reopened)
    assert before["ok"] and after["ok"]
    assert canonical_json(restarted.current_state()) == canonical_json(reopened.load_state())
    assert restarted.current_state()["habitat"]["consequence_memory"]["schema"] == CONSEQUENCE_MEMORY_SCHEMA
    reopened.close()
