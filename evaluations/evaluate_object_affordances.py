#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import Simulation
from terrarium.models import OBJECT_AFFORDANCE_SCHEMA, initial_state, object_affordances

FIXED = "2026-01-01T00:00:00Z"
SEEDS = (1701, 1702, 42, 999)


def _run(seed: int, steps: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    state = initial_state(seed, created_at=FIXED)
    sim = Simulation()
    rows: list[dict[str, Any]] = []
    for _ in range(steps):
        _, _, details, state = sim.step(state)
        if details.get("decision"):
            rows.append(deepcopy(details))
    return state, rows


def _follow_rate(rows: list[dict[str, Any]], source: str, target: str) -> tuple[int, float]:
    sources = [(i, row) for i, row in enumerate(rows) if row.get("object_affordance") == source]
    matched = sum(
        any(
            candidate.get("object_id") == row.get("object_id") and candidate.get("object_affordance") == target
            for candidate in rows[i + 1:i + 3]
        )
        for i, row in sources
    )
    return len(sources), round(matched / len(sources), 6) if sources else 0.0


def evaluate_seed(seed: int, steps: int) -> dict[str, Any]:
    final, rows = _run(seed, steps)
    object_rows = [row for row in rows if row.get("object_id")]
    affordance_counts = Counter(str(row.get("object_affordance")) for row in object_rows if row.get("object_affordance"))
    by_object: dict[str, Counter[str]] = defaultdict(Counter)
    by_archetype: dict[str, Counter[str]] = defaultdict(Counter)
    for row in object_rows:
        affordance = row.get("object_affordance")
        if affordance:
            by_object[str(row["object_id"])][str(affordance)] += 1
            by_archetype[str(row.get("object_archetype"))][str(affordance)] += 1

    roll_count, roll_retrieve_rate = _follow_rate(rows, "roll", "retrieve")
    tug_count, tug_nest_rate = _follow_rate(rows, "tug", "nest")
    illegal_nudges = [
        row for row in rows
        if row.get("action") == "nudge" and row.get("object_archetype") not in {"rolling", "soft_nesting"}
    ]
    final_objects = {
        str(obj["id"]): {
            "archetype": str(obj["archetype"]),
            "interaction_state": str(obj["interaction_state"]),
            "state_transitions": int(obj.get("state_transitions", 0)),
            "available_affordances": list(object_affordances(obj)),
            "times_nudged": int(obj.get("times_nudged", 0)),
            "times_moved": int(obj.get("times_moved", 0)),
        }
        for obj in final["objects"]
    }
    interacted_archetypes = {str(row.get("object_archetype")) for row in object_rows if row.get("object_archetype")}
    checks = {
        "object_schema_recorded": all(row.get("object_affordance_schema") == OBJECT_AFFORDANCE_SCHEMA for row in object_rows),
        "all_four_archetypes_interacted": interacted_archetypes == {"rolling", "soft_nesting", "delicate", "keepsake"},
        "no_illegal_nudges": not illegal_nudges,
        "rolling_play_exercised": roll_count >= 10,
        "rolls_create_retrieval_chains": roll_retrieve_rate >= 0.90,
        "soft_tug_exercised": tug_count >= 3,
        "tugs_create_nesting_chains": tug_nest_rate >= 0.75,
        "display_state_exercised": int(affordance_counts.get("display", 0)) >= 5,
        "delicate_and_keepsakes_never_nudged": all(
            final_objects[oid]["times_nudged"] == 0 for oid in ("amber_leaf", "shell", "glass_star")
        ),
        "persistent_state_transitions_exercised": all(obj["state_transitions"] > 0 for obj in final_objects.values()),
        "stateful_affordance_subsets_survive_long_run": (
            "nudge" in final_objects["blue_stone"]["available_affordances"]
            and "nudge" not in final_objects["amber_leaf"]["available_affordances"]
            and "nudge" not in final_objects["shell"]["available_affordances"]
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "decision_events": len(rows),
            "object_decisions": len(object_rows),
            "affordance_counts": dict(sorted(affordance_counts.items())),
            "by_object": {key: dict(sorted(value.items())) for key, value in sorted(by_object.items())},
            "by_archetype": {key: dict(sorted(value.items())) for key, value in sorted(by_archetype.items())},
            "roll_retrieve_within_two_rate": roll_retrieve_rate,
            "tug_nest_within_two_rate": tug_nest_rate,
            "illegal_nudges": len(illegal_nudges),
            "final_objects": final_objects,
        },
    }


def evaluate(steps: int) -> dict[str, Any]:
    results = {str(seed): evaluate_seed(seed, steps) for seed in SEEDS}
    controlled = initial_state(1701, created_at=FIXED)
    controlled_objects = {obj["id"]: obj for obj in controlled["objects"]}
    controlled_checks = {
        "rolling_and_delicate_differ": (
            set(object_affordances(controlled_objects["blue_stone"])) == {"inspect", "carry", "nudge"}
            and set(object_affordances(controlled_objects["amber_leaf"])) == {"inspect", "carry"}
        ),
        "rumpled_thread_unlocks_nest": False,
        "rolled_object_blocks_repeat_roll": False,
    }
    controlled_objects["red_thread"]["interaction_state"] = "rumpled"
    controlled_checks["rumpled_thread_unlocks_nest"] = set(object_affordances(controlled_objects["red_thread"])) == {"inspect", "carry", "nest"}
    controlled_objects["blue_stone"]["interaction_state"] = "rolled"
    controlled_checks["rolled_object_blocks_repeat_roll"] = set(object_affordances(controlled_objects["blue_stone"])) == {"inspect", "carry"}
    return {
        "schema": "terrarium.object-affordance-evaluation.v1",
        "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
        "seeds": list(SEEDS),
        "steps_per_seed": steps,
        "controlled_checks": controlled_checks,
        "results": results,
        "all_passed": all(controlled_checks.values()) and all(row["passed"] for row in results.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10080)
    parser.add_argument("--out", default="artifacts/object-affordance-evaluation.json")
    args = parser.parse_args()
    result = evaluate(args.steps)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
