#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluations.evaluate_coherence import evaluate as evaluate_coherence
from terrarium.engine import Simulation
from terrarium.models import HABIT_CONTEXTS, HABIT_PROFILE_SCHEMA, ZONES, canonical_json, initial_state

FIXED = "2026-01-01T00:00:00Z"
MOVEMENT = {"walk", "explore"}
OBJECT_SELECTION = {"inspect", "carry"}


def _run(seed: int, steps: int, *, state: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    current = deepcopy(state) if state is not None else initial_state(seed, created_at=FIXED)
    sim = Simulation()
    rows: list[dict[str, Any]] = []
    for _ in range(steps):
        _, _, details, current = sim.step(current)
        if details.get("decision"):
            rows.append({
                "tick": int(current["tick"]),
                "world_minutes": int(current["world_minutes"]),
                "day": int((int(current["world_minutes"]) - 420) // 1440),
                "lighting": str(current["habitat"]["lighting"]),
                "action": str(details.get("action")),
                "zone": str(current["creature"]["zone"]),
                "to_zone": details.get("to_zone"),
                "travel_purpose": details.get("travel_purpose"),
                "object_id": details.get("object_id"),
            })
    return current, rows


def _share(counter: Counter[str], key: str) -> float:
    total = sum(counter.values())
    return 0.0 if total <= 0 else counter[key] / total


def _top_share(counter: Counter[str]) -> float:
    total = sum(counter.values())
    return 0.0 if total <= 0 else max(counter.values()) / total


def _physical_signature(state: dict[str, Any]) -> str:
    copy = deepcopy(state)
    copy["creature"].pop("habit_profile", None)
    return canonical_json(copy)


def _profile_is_valid(state: dict[str, Any]) -> bool:
    p = state["creature"].get("habit_profile") or {}
    if p.get("schema") != HABIT_PROFILE_SCHEMA:
        return False
    if set(p.get("zone_affinity", {})) != set(ZONES):
        return False
    object_ids = {str(obj["id"]) for obj in state["objects"]}
    if set(p.get("object_affinity", {})) != object_ids:
        return False
    contexts = p.get("context_zone_affinity", {})
    if set(contexts) != set(HABIT_CONTEXTS):
        return False
    if any(set(values) != set(ZONES) for values in contexts.values()):
        return False
    values = list(p["zone_affinity"].values()) + list(p["object_affinity"].values())
    for context in HABIT_CONTEXTS:
        values.extend(contexts[context].values())
    return all(0.0 <= float(value) <= 1.0 for value in values)


def _controlled_profile(base: dict[str, Any], *, zone: str, object_id: str) -> dict[str, Any]:
    state = deepcopy(base)
    profile = state["creature"]["habit_profile"]
    profile["experience_count"] = 2200
    profile["migration_origin"] = "controlled-history-fixture"
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
    return state


def _future_counts(rows: list[dict[str, Any]]) -> tuple[Counter[str], Counter[str], Counter[str]]:
    destinations = Counter(
        str(row["to_zone"])
        for row in rows
        if row["action"] in MOVEMENT and row["travel_purpose"] != "object_delivery" and row["to_zone"]
    )
    objects = Counter(
        str(row["object_id"])
        for row in rows
        if row["action"] in OBJECT_SELECTION and row["object_id"]
    )
    actions = Counter(str(row["action"]) for row in rows)
    return destinations, objects, actions


def evaluate(seed: int = 1701, steps: int = 10080) -> dict[str, Any]:
    final, rows = _run(seed, steps)
    final2, rows2 = _run(seed, steps)
    profile = final["creature"]["habit_profile"]
    destinations, objects, actions = _future_counts(rows)

    split = max(1, int(steps * 5 / 7))
    trained, _ = _run(seed, split)
    trained_profile = deepcopy(trained["creature"]["habit_profile"])
    future, future_rows = _run(seed, steps - split, state=trained)
    future_destinations, future_objects, _ = _future_counts(future_rows)
    favorite_zone = max(trained_profile["zone_affinity"], key=trained_profile["zone_affinity"].get)
    favorite_object = max(trained_profile["object_affinity"], key=trained_profile["object_affinity"].get)

    # Causal choice probes hold the physical opportunity set and deterministic
    # random draws constant while neutralizing only the learned preference map.
    # This isolates preference influence from object relocation, sleep pressure,
    # weather, and other legitimate environmental constraints in the full world.
    neutral_profile = deepcopy(trained_profile)
    for values in [neutral_profile["zone_affinity"], neutral_profile["object_affinity"]]:
        mean = sum(float(value) for value in values.values()) / len(values)
        for key in values:
            values[key] = mean
    for context in HABIT_CONTEXTS:
        values = neutral_profile["context_zone_affinity"][context]
        mean = sum(float(value) for value in values.values()) / len(values)
        for key in values:
            values[key] = mean

    probe = Simulation()
    probe_objects = []
    for obj in trained["objects"]:
        candidate = deepcopy(obj)
        candidate["state"] = "placed"
        candidate["carried_by"] = None
        probe_objects.append(candidate)
    object_pref_counts: Counter[str] = Counter()
    object_neutral_counts: Counter[str] = Counter()
    zone_pref_counts: Counter[str] = Counter()
    zone_neutral_counts: Counter[str] = Counter()
    probe_zone = next(name for name in ZONES if name != favorite_zone)
    probe_context = {"recent_zones": [probe_zone], "recent_objects": [], "intent": None}
    probe_state = deepcopy(trained)
    probe_state["creature"]["zone"] = probe_zone
    for sample in range(2400):
        object_pref_counts[probe._choose_object(random.Random(sample), probe_objects, probe_context, habit_profile=trained_profile)["id"]] += 1
        object_neutral_counts[probe._choose_object(random.Random(sample), probe_objects, probe_context, habit_profile=neutral_profile)["id"]] += 1
        phase = HABIT_CONTEXTS[sample % len(HABIT_CONTEXTS)]
        probe_state["habitat"]["lighting"] = phase
        zone_pref_counts[probe._choose_destination(random.Random(sample), probe_state, probe_context, zone=probe_zone, carrying=None, habit_profile=trained_profile)] += 1
        zone_neutral_counts[probe._choose_destination(random.Random(sample), probe_state, probe_context, zone=probe_zone, carrying=None, habit_profile=neutral_profile)] += 1
    learned_zone_choice_uplift = _share(zone_pref_counts, favorite_zone) - _share(zone_neutral_counts, favorite_zone)
    learned_object_choice_uplift = _share(object_pref_counts, favorite_object) - _share(object_neutral_counts, favorite_object)

    day_destinations: dict[int, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row["action"] in MOVEMENT and row["travel_purpose"] != "object_delivery" and row["to_zone"]:
            day_destinations[int(row["day"])][str(row["to_zone"])] += 1
    day_vectors = [tuple(counter.get(zone, 0) for zone in ZONES) for _, counter in sorted(day_destinations.items())]

    base = initial_state(seed, created_at=FIXED)
    history_a = _controlled_profile(base, zone="window", object_id="amber_leaf")
    history_b = _controlled_profile(base, zone="activity_corner", object_id="acorn")
    physical_equivalent = _physical_signature(history_a) == _physical_signature(history_b)
    a1, a_rows1 = _run(seed, 2400, state=history_a)
    a2, a_rows2 = _run(seed, 2400, state=history_a)
    b1, b_rows1 = _run(seed, 2400, state=history_b)
    b2, b_rows2 = _run(seed, 2400, state=history_b)
    a_dest, a_obj, a_actions = _future_counts(a_rows1)
    b_dest, b_obj, b_actions = _future_counts(b_rows1)

    controlled = {
        "physical_state_equal_before_run": physical_equivalent,
        "history_a": {
            "favorite_zone": "window",
            "favorite_zone_future_share": round(_share(a_dest, "window"), 6),
            "favorite_object": "amber_leaf",
            "favorite_object_future_share": round(_share(a_obj, "amber_leaf"), 6),
            "destination_counts": dict(sorted(a_dest.items())),
            "object_counts": dict(sorted(a_obj.items())),
        },
        "history_b": {
            "favorite_zone": "activity_corner",
            "favorite_zone_future_share": round(_share(b_dest, "activity_corner"), 6),
            "favorite_object": "acorn",
            "favorite_object_future_share": round(_share(b_obj, "acorn"), 6),
            "destination_counts": dict(sorted(b_dest.items())),
            "object_counts": dict(sorted(b_obj.items())),
        },
        "a_deterministic": canonical_json(a1) == canonical_json(a2) and a_rows1 == a_rows2,
        "b_deterministic": canonical_json(b1) == canonical_json(b2) and b_rows1 == b_rows2,
        "future_profiles_diverge": canonical_json(a1["creature"]["habit_profile"]) != canonical_json(b1["creature"]["habit_profile"]),
        "favorite_zone_cross_advantage": round(
            (_share(a_dest, "window") - _share(b_dest, "window"))
            + (_share(b_dest, "activity_corner") - _share(a_dest, "activity_corner")), 6
        ),
    }

    zone_values = list(profile["zone_affinity"].values())
    object_values = list(profile["object_affinity"].values())
    metrics = {
        "decision_events": len(rows),
        "habit_experience_count": int(profile["experience_count"]),
        "zone_affinity_range": round(max(zone_values) - min(zone_values), 6),
        "object_affinity_range": round(max(object_values) - min(object_values), 6),
        "non_delivery_destination_counts": dict(sorted(destinations.items())),
        "top_non_delivery_destination_share": round(_top_share(destinations), 6),
        "object_selection_counts": dict(sorted(objects.items())),
        "top_object_selection_share": round(_top_share(objects), 6),
        "decision_action_counts": dict(sorted(actions.items())),
        "action_classes": len(actions),
        "zones_selected": len(destinations),
        "days_with_autonomous_travel": len(day_vectors),
        "distinct_day_destination_vectors": len(set(day_vectors)),
        "trained_favorite_zone": favorite_zone,
        "trained_favorite_zone_future_share": round(_share(future_destinations, favorite_zone), 6),
        "trained_favorite_object": favorite_object,
        "trained_favorite_object_future_share": round(_share(future_objects, favorite_object), 6),
        "learned_favorite_zone_controlled_choice_uplift": round(learned_zone_choice_uplift, 6),
        "learned_favorite_object_controlled_choice_uplift": round(learned_object_choice_uplift, 6),
        "future_top_destination_share": round(_top_share(future_destinations), 6),
        "future_top_object_share": round(_top_share(future_objects), 6),
    }

    coherence = evaluate_coherence(seed, 2000)
    checks = {
        "deterministic_duplicate_run": canonical_json(final) == canonical_json(final2) and rows == rows2,
        "profile_schema_and_references_valid": _profile_is_valid(final),
        "preferences_are_bounded": _profile_is_valid(final),
        "preferences_change_over_time": metrics["habit_experience_count"] >= 1000 and metrics["zone_affinity_range"] >= 0.06 and metrics["object_affinity_range"] >= 0.06,
        "all_action_classes_remain_available": metrics["action_classes"] >= 9,
        "all_zones_remain_explored": metrics["zones_selected"] == len(ZONES),
        "zone_habit_does_not_lock_in": metrics["top_non_delivery_destination_share"] <= 0.42,
        "object_habit_does_not_lock_in": metrics["top_object_selection_share"] <= 0.38,
        "days_retain_variation": metrics["days_with_autonomous_travel"] >= 6 and metrics["distinct_day_destination_vectors"] >= 5,
        "learned_zone_preference_causes_choice_uplift": metrics["learned_favorite_zone_controlled_choice_uplift"] >= 0.003,
        "learned_object_preference_causes_choice_uplift": metrics["learned_favorite_object_controlled_choice_uplift"] >= 0.012,
        "controlled_worlds_begin_physically_equivalent": controlled["physical_state_equal_before_run"],
        "controlled_histories_are_each_deterministic": controlled["a_deterministic"] and controlled["b_deterministic"],
        "controlled_histories_diverge": controlled["future_profiles_diverge"] and controlled["favorite_zone_cross_advantage"] >= 0.12,
        "controlled_window_history_remains_a_tendency": 0.24 <= controlled["history_a"]["favorite_zone_future_share"] <= 0.50,
        "controlled_activity_history_remains_a_tendency": 0.24 <= controlled["history_b"]["favorite_zone_future_share"] <= 0.50,
        "iteration4_short_horizon_coherence_preserved": bool(coherence["passed"]),
    }
    return {
        "schema": "terrarium.long-horizon-habit-evaluation.v1",
        "seed": seed,
        "steps": steps,
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": metrics,
        "controlled_history_divergence": controlled,
        "short_horizon_coherence": coherence,
        "final_habit_profile": profile,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--steps", type=int, default=10080)
    parser.add_argument("--out")
    args = parser.parse_args()
    result = evaluate(args.seed, args.steps)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
