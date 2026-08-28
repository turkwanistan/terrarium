#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.consequences import (
    CONSEQUENCE_MEMORY_LIMIT,
    CONSEQUENCE_MEMORY_SCHEMA,
    consequence_opportunities,
    ensure_consequence_memory,
    record_consequence,
)
from terrarium.engine import Simulation, WorldEngine
from terrarium.frame import make_frame
from terrarium.models import canonical_json, initial_state, seasonal_clock_for
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore

FIXED = "2026-01-01T00:00:00Z"
SEEDS = (1701, 1702, 42, 999)
VALID_OBJECT_STATES = {
    "rolling": {"settled", "rolled"},
    "soft_nesting": {"loose", "rumpled", "nested"},
    "delicate": {"fresh", "handled"},
    "keepsake": {"handled", "displayed"},
}


def _possession_ok(state: dict[str, Any]) -> bool:
    creature = state["creature"]
    carried = [obj for obj in state["objects"] if obj.get("state") == "carried"]
    carrying = creature.get("carrying")
    if carrying is None:
        return not carried and all(obj.get("carried_by") is None for obj in state["objects"])
    return (
        len(carried) == 1
        and str(carried[0]["id"]) == str(carrying)
        and str(carried[0].get("carried_by")) == str(creature["id"])
    )


def _objects_ok(state: dict[str, Any]) -> bool:
    for obj in state["objects"]:
        archetype = str(obj.get("archetype"))
        interaction = str(obj.get("interaction_state"))
        if interaction not in VALID_OBJECT_STATES.get(archetype, set()):
            return False
        if archetype == "soft_nesting" and interaction == "nested" and str(obj.get("zone")) not in {"open_space", "sleeping_nook"}:
            return False
    return True


def _run(seed: int, steps: int) -> dict[str, Any]:
    state = initial_state(seed, created_at=FIXED)
    sim = Simulation()
    decisions = 0
    action_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    source_causes: Counter[str] = Counter()
    recognized_ages: list[int] = []
    chain_start: dict[str, int] = {}
    chain_durations: list[int] = []
    possession_violations = 0
    object_state_violations = 0
    max_entries = 0
    max_open_intent_ticks = 0
    active_intent_ticks = 0

    for _ in range(steps):
        _, _, details, state = sim.step(state)
        if details.get("decision"):
            decisions += 1
            action_counts[str(details.get("action"))] += 1
        role = details.get("consequence_role")
        memory_id = details.get("consequence_memory_id")
        if role:
            role_counts[str(role)] += 1
            if details.get("consequence_kind"):
                kind_counts[str(details["consequence_kind"])] += 1
            source = details.get("consequence_source") or {}
            if source.get("cause"):
                source_causes[str(source["cause"])] += 1
            if role == "recognize" and memory_id:
                chain_start[str(memory_id)] = int(state["tick"])
                created_minute = details.get("consequence_created_world_minute")
                if created_minute is not None:
                    recognized_ages.append(int(state["world_minutes"]) - int(created_minute))
            elif role == "engage" and memory_id and str(memory_id) in chain_start:
                chain_durations.append(int(state["tick"]) - chain_start.pop(str(memory_id)))

        intent = (state["creature"].get("behavior_context") or {}).get("intent") or {}
        if intent.get("kind") == "consequence_revisit":
            active_intent_ticks += 1
            max_open_intent_ticks = max(max_open_intent_ticks, active_intent_ticks)
        else:
            active_intent_ticks = 0
        if not _possession_ok(state):
            possession_violations += 1
        if not _objects_ok(state):
            object_state_violations += 1
        max_entries = max(max_entries, len(state["habitat"]["consequence_memory"]["entries"]))

    memory = state["habitat"]["consequence_memory"]
    recognition_share = role_counts["recognize"] / max(1, decisions)
    quiet_actions = sum(action_counts[name] for name in ("idle", "rest", "loaf", "groom", "stretch", "sleep", "wake"))
    quiet_share = quiet_actions / max(1, decisions)
    checks = {
        "schema_preserved": memory.get("schema") == CONSEQUENCE_MEMORY_SCHEMA,
        "causal_entries_created": int(memory.get("created_count", 0)) >= 8,
        "later_revisits_occur": int(memory.get("revisit_count", 0)) >= 1,
        "bounded_storage": max_entries <= CONSEQUENCE_MEMORY_LIMIT and len(memory.get("entries") or []) <= CONSEQUENCE_MEMORY_LIMIT,
        "recognition_is_later_not_immediate": bool(recognized_ages) and min(recognized_ages) >= 45,
        "multi_stage_chain_exercised": role_counts["recognize"] >= 1 and role_counts["engage"] >= 1,
        "approach_stage_exercised": role_counts["approach"] >= 1,
        "chains_remain_bounded": bool(chain_durations) and max(chain_durations) <= 20 and max_open_intent_ticks <= 20,
        "no_situation_spam": recognition_share <= 0.04,
        "ordinary_quiet_behavior_survives": quiet_share >= 0.30,
        "possession_integrity": possession_violations == 0,
        "object_state_integrity": object_state_violations == 0,
        "multiple_causal_sources_compose": len(kind_counts) >= 2 and len(source_causes) >= 2,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "steps": steps,
            "decisions": decisions,
            "action_counts": dict(sorted(action_counts.items())),
            "consequence_role_counts": dict(sorted(role_counts.items())),
            "consequence_kind_counts": dict(sorted(kind_counts.items())),
            "source_causes": dict(sorted(source_causes.items())),
            "recognized_age_minutes_min": min(recognized_ages) if recognized_ages else None,
            "recognized_age_minutes_max": max(recognized_ages) if recognized_ages else None,
            "chain_duration_ticks_max": max(chain_durations) if chain_durations else None,
            "recognition_share_of_decisions": round(recognition_share, 6),
            "quiet_action_share": round(quiet_share, 6),
            "created_count": int(memory.get("created_count", 0)),
            "revisit_count": int(memory.get("revisit_count", 0)),
            "resolved_count": int(memory.get("resolved_count", 0)),
            "final_open_entries": len(memory.get("entries") or []),
            "max_open_entries": max_entries,
            "possession_violations": possession_violations,
            "object_state_violations": object_state_violations,
        },
    }


def _controlled_history_sensitivity() -> dict[str, Any]:
    with_history = initial_state(1701, created_at=FIXED)
    without_history = deepcopy(with_history)
    entry = record_consequence(
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
    same_present_frame = canonical_json(make_frame(with_history)) == canonical_json(make_frame(without_history))
    opportunity_a = consequence_opportunities(with_history)
    opportunity_repeat = consequence_opportunities(deepcopy(with_history))
    opportunity_b = consequence_opportunities(without_history)

    left = deepcopy(with_history)
    right = deepcopy(without_history)
    sim_left = Simulation()
    sim_right = Simulation()
    visible_equal_until_controlled_recognition = True
    divergence_tick: int | None = None
    for _ in range(2200):
        _, _, details_left, left = sim_left.step(left)
        _, _, _, right = sim_right.step(right)
        if details_left.get("consequence_memory_id") == entry["id"] and details_left.get("consequence_role") == "recognize":
            divergence_tick = int(left["tick"])
            break
        if canonical_json(make_frame(left)) != canonical_json(make_frame(right)):
            visible_equal_until_controlled_recognition = False
            break

    deterministic_a = deepcopy(with_history)
    deterministic_b = deepcopy(with_history)
    sim_a = Simulation()
    sim_b = Simulation()
    deterministic = True
    for _ in range(900):
        row_a = sim_a.step(deterministic_a)
        row_b = sim_b.step(deterministic_b)
        deterministic_a = row_a[3]
        deterministic_b = row_b[3]
        if canonical_json(deterministic_a) != canonical_json(deterministic_b) or row_a[:3] != row_b[:3]:
            deterministic = False
            break

    return {
        "same_immediate_visible_frame": same_present_frame,
        "different_causal_opportunity_sets": bool(opportunity_a) and opportunity_a == opportunity_repeat and opportunity_b == [],
        "visible_equal_until_controlled_recognition": visible_equal_until_controlled_recognition,
        "controlled_history_changes_later_future": divergence_tick is not None,
        "divergence_tick": divergence_tick,
        "individual_determinism": deterministic,
        "controlled_memory_id": entry["id"],
    }


def _context_composition() -> dict[str, Any]:
    spring = initial_state(1701, created_at=FIXED)
    entry = record_consequence(
        spring,
        kind="situational_aftermath",
        zone="window",
        strength=0.8,
        source={"cause": "controlled-season-context", "season": "spring", "weather": "clear"},
        min_delay_minutes=1,
    )
    spring["world_minutes"] += 2
    summer = deepcopy(spring)
    summer["habitat"]["seasonal_clock"] = seasonal_clock_for(
        FIXED,
        "2026-01-23T00:00:00Z",
        migration_origin="fixture",
    )
    spring_score = next(item["score"] for item in consequence_opportunities(spring) if item["memory_id"] == entry["id"])
    summer_score = next(item["score"] for item in consequence_opportunities(summer) if item["memory_id"] == entry["id"])
    return {
        "season_context_is_available": spring_score > summer_score,
        "spring_score": spring_score,
        "summer_score": summer_score,
    }


def _replay_authority() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="terrarium-iteration9-") as temp:
        store = WorldStore(temp)
        engine = WorldEngine(store, seed=1701, snapshot_every=20)
        engine.run_steps(1200)
        before = engine.current_state()
        replay_before = assert_exact_replay(store)
        store.close()

        reopened = WorldStore(temp)
        restarted = WorldEngine(reopened, seed=999)
        replay_after = assert_exact_replay(reopened)
        after = restarted.current_state()
        reopened.close()
    renderer_source = (PROJECT_ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    return {
        "exact_replay_before_restart": bool(replay_before["ok"]),
        "exact_replay_after_restart": bool(replay_after["ok"]),
        "restart_state_exact": canonical_json(before) == canonical_json(after),
        "canonical_memory_survives": (after["habitat"].get("consequence_memory") or {}).get("schema") == CONSEQUENCE_MEMORY_SCHEMA,
        "renderer_has_no_private_consequence_store": "consequence_memory" not in renderer_source,
        "canonical_state_hash": replay_after["canonical_state_hash"],
    }


def _migration_check() -> dict[str, Any]:
    state = initial_state(1701, created_at=FIXED)
    state["habitat"].pop("consequence_memory")
    objects = canonical_json(state["objects"])
    habits = canonical_json(state["creature"]["habit_profile"])
    memory = ensure_consequence_memory(state)
    return {
        "neutral_existing_world": memory.get("migration_origin") == "neutral-existing-world",
        "no_fabricated_entries": memory.get("entries") == [],
        "objects_unchanged": canonical_json(state["objects"]) == objects,
        "habits_unchanged": canonical_json(state["creature"]["habit_profile"]) == habits,
    }


def evaluate(steps: int = 10080, seeds: tuple[int, ...] = SEEDS) -> dict[str, Any]:
    controlled = _controlled_history_sensitivity()
    context = _context_composition()
    replay = _replay_authority()
    migration = _migration_check()
    results = {str(seed): _run(seed, steps) for seed in seeds}
    controlled_passed = all(value for key, value in controlled.items() if key not in {"divergence_tick", "controlled_memory_id"})
    context_passed = bool(context["season_context_is_available"])
    replay_passed = all(value for key, value in replay.items() if key != "canonical_state_hash")
    migration_passed = all(migration.values())
    return {
        "schema": "terrarium.consequence-evaluation.v1",
        "consequence_memory_schema": CONSEQUENCE_MEMORY_SCHEMA,
        "steps_per_seed": steps,
        "seeds": list(seeds),
        "controlled_history_sensitivity": controlled,
        "context_composition": context,
        "replay_authority": replay,
        "migration": migration,
        "results": results,
        "all_passed": controlled_passed and context_passed and replay_passed and migration_passed and all(row["passed"] for row in results.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10080)
    parser.add_argument("--seeds", default=",".join(str(seed) for seed in SEEDS))
    parser.add_argument("--out", default="artifacts/consequence-evaluation.json")
    args = parser.parse_args()
    seeds = tuple(int(value.strip()) for value in args.seeds.split(",") if value.strip())
    result = evaluate(args.steps, seeds)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
