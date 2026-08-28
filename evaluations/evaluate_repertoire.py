#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import Simulation
from terrarium.models import HABIT_CONTEXTS, ZONES, canonical_json, initial_state

FIXED = "2026-01-01T00:00:00Z"
SEEDS = (1701, 1702, 42, 999)
OLD_GENERIC = {"idle", "rest", "walk", "explore", "sleep", "wake"}
OLD_ACTIONS = {"idle", "rest", "walk", "explore", "inspect", "carry", "place", "look_outside", "sleep", "wake"}
NEW_ACTIONS = {"loaf", "groom", "stretch", "nudge", "react"}
EXPECTED_FAMILIES = {"idle", "comfort", "self_care", "travel", "investigate", "arrange", "play", "observe", "react", "sleep"}


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counter.values())


def _max_run(values: list[str], *, exclude: set[str] | None = None) -> int:
    exclude = exclude or set()
    best = run = 0
    current = None
    for value in values:
        if value in exclude:
            current = None; run = 0; continue
        if value == current:
            run += 1
        else:
            current, run = value, 1
        best = max(best, run)
    return best


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


def _run(seed: int, steps: int, *, state: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    current = deepcopy(state) if state is not None else initial_state(seed, created_at=FIXED)
    sim = Simulation()
    rows: list[dict[str, Any]] = []
    for _ in range(steps):
        before = current
        _, _, details, current = sim.step(current)
        if not details.get("decision"):
            continue
        action = str(details.get("action"))
        family = str(details.get("activity_family") or Simulation._activity_family(action))
        rows.append({
            "tick": int(current["tick"]),
            "action": action,
            "family": family,
            "zone": str(current["creature"]["zone"]),
            "from_zone": details.get("from_zone"),
            "to_zone": details.get("to_zone"),
            "travel_purpose": details.get("travel_purpose"),
            "object_id": details.get("object_id"),
            "world_event_id": details.get("world_event_id"),
            "world_event_type": details.get("world_event_type"),
            "consequence_memory_id": details.get("consequence_memory_id"),
            "consequence_role": details.get("consequence_role"),
            "object_affordance": details.get("object_affordance"),
            "target_x": details.get("target_x"),
            "target_y": details.get("target_y"),
            "result_x": details.get("result_x"),
            "result_y": details.get("result_y"),
            "before_object": next((
                (str(obj["zone"]), int(obj["x"]), int(obj["y"]))
                for obj in before["objects"] if obj["id"] == details.get("object_id")
            ), None),
        })
    return current, rows


def _sequence_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    inspected = [(i, row) for i, row in enumerate(rows) if row["action"] == "inspect" and row["object_id"]]
    inspect_followups = sum(
        any(candidate["object_id"] == row["object_id"] and candidate["action"] in {"carry", "nudge"}
            for candidate in rows[i + 1:i + 3])
        for i, row in inspected
    )
    nudges = [(i, row) for i, row in enumerate(rows) if row["action"] == "nudge" and row["object_id"]]
    nudge_reinspections = sum(
        any(candidate["object_id"] == row["object_id"] and candidate["action"] == "inspect"
            for candidate in rows[i + 1:i + 3])
        for i, row in nudges
    )
    nudge_causal_followups = sum(
        any(
            candidate["object_id"] == row["object_id"]
            and (
                (row.get("object_affordance") == "tug" and candidate.get("object_affordance") == "nest")
                or (row.get("object_affordance") != "tug" and candidate["action"] == "inspect")
            )
            for candidate in rows[i + 1:i + 3]
        )
        for i, row in nudges
    )
    weather = [
        (i, row) for i, row in enumerate(rows)
        if row["action"] == "react" and not row.get("world_event_id") and not row.get("consequence_memory_id")
    ]
    weather_window_followups = sum(
        any(candidate["action"] in {"walk", "explore"} and candidate["to_zone"] == "window"
            for candidate in rows[i + 1:i + 3])
        for i, _ in weather
    )
    return {
        "inspect_sessions": len(inspected),
        "inspect_to_manipulation_within_two_rate": round(inspect_followups / len(inspected), 6) if inspected else 0.0,
        "nudge_sessions": len(nudges),
        "nudge_to_reinspect_within_two_rate": round(nudge_reinspections / len(nudges), 6) if nudges else 0.0,
        "nudge_to_causal_followup_within_two_rate": round(nudge_causal_followups / len(nudges), 6) if nudges else 0.0,
        "weather_reactions": len(weather),
        "weather_reaction_to_window_within_two_rate": round(weather_window_followups / len(weather), 6) if weather else 1.0,
    }


def _summarize(final: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    actions = Counter(row["action"] for row in rows)
    families = Counter(row["family"] for row in rows)
    family_sequence = [row["family"] for row in rows]
    transitions = {(a, b) for a, b in zip(family_sequence, family_sequence[1:]) if a != b}
    combos = {(row["zone"], row["family"]) for row in rows}
    nudge_patterns = {
        (str(row["object_id"]), row["before_object"], int(row["result_x"]), int(row["result_y"]))
        for row in rows if row["action"] == "nudge" and row["object_id"] and row["result_x"] is not None and row["before_object"]
    }
    arrangement_patterns = {
        (str(row["object_id"]), str(row["from_zone"]), str(row["zone"]))
        for row in rows if row["action"] == "place" and row["object_id"]
    }
    deltas = [b["tick"] - a["tick"] for a, b in zip(rows, rows[1:])]
    generic = sum(actions[action] for action in OLD_GENERIC)
    new = sum(actions[action] for action in NEW_ACTIONS)
    history = final["habitat"]["affordance_history"]
    arrangements = Counter(
        str(obj["zone"]) for obj in final["objects"] if int(obj.get("times_moved", 0)) > 0
    )
    return {
        "decision_events": len(rows),
        "action_counts": dict(sorted(actions.items())),
        "family_counts": dict(sorted(families.items())),
        "meaningful_activity_families": len(families),
        "family_entropy_bits": round(entropy(families), 6),
        "distinct_family_transitions": len(transitions),
        "distinct_zone_family_combinations": len(combos),
        "max_non_sleep_family_streak": _max_run(family_sequence, exclude={"sleep"}),
        "old_generic_decision_share": round(generic / len(rows), 6) if rows else 0.0,
        "new_action_decision_share": round(new / len(rows), 6) if rows else 0.0,
        "top_family_share": round(max(families.values()) / len(rows), 6) if rows else 0.0,
        "average_activity_ticks": round(sum(deltas) / len(deltas), 6) if deltas else 0.0,
        "new_actions_seen": sorted(NEW_ACTIONS & set(actions)),
        "old_actions_seen": sorted(OLD_ACTIONS & set(actions)),
        "distinct_nudge_patterns": len(nudge_patterns),
        "distinct_arrangement_patterns": len(arrangement_patterns),
        "objects_nudged": sum(int(obj.get("times_nudged", 0)) > 0 for obj in final["objects"]),
        "object_nudges": sum(int(obj.get("times_nudged", 0)) for obj in final["objects"]),
        "objects_moved": sum(int(obj.get("times_moved", 0)) > 0 for obj in final["objects"]),
        "object_moves": sum(int(obj.get("times_moved", 0)) for obj in final["objects"]),
        "final_arrangement_zones": dict(sorted(arrangements.items())),
        "zones_with_arrangement_history": sum(int(v) > 0 for v in history["zone_arrangements"].values()),
        "zones_with_comfort_history": sum(int(v) > 0 for v in history["zone_comfort"].values()),
        "completed_family_history": dict(sorted(history["completed_families"].items())),
        **_sequence_metrics(rows),
    }


def _history_divergence(seed: int = 1701, steps: int = 3000) -> dict[str, Any]:
    base = initial_state(seed, created_at=FIXED)
    a0 = _controlled_profile(base, zone="window", object_id="amber_leaf")
    b0 = _controlled_profile(base, zone="activity_corner", object_id="acorn")
    a_physical = deepcopy(a0); b_physical = deepcopy(b0)
    a_physical["creature"].pop("habit_profile", None); b_physical["creature"].pop("habit_profile", None)
    a1, ar1 = _run(seed, steps, state=a0); a2, ar2 = _run(seed, steps, state=a0)
    b1, br1 = _run(seed, steps, state=b0); b2, br2 = _run(seed, steps, state=b0)

    def patterns(rows: list[dict[str, Any]], zone: str, object_id: str) -> dict[str, Any]:
        comfort = Counter(row["zone"] for row in rows if row["family"] == "comfort")
        loaf = Counter(row["zone"] for row in rows if row["action"] == "loaf")
        placements = Counter(row["zone"] for row in rows if row["action"] == "place")
        nudges = Counter(str(row["object_id"]) for row in rows if row["action"] == "nudge" and row["object_id"])
        return {
            "favorite_zone": zone,
            "favorite_object": object_id,
            "comfort_counts": dict(sorted(comfort.items())),
            "loaf_counts": dict(sorted(loaf.items())),
            "placement_counts": dict(sorted(placements.items())),
            "nudge_counts": dict(sorted(nudges.items())),
            "favorite_zone_comfort_share": round(comfort[zone] / max(1, sum(comfort.values())), 6),
            "favorite_zone_loaf_share": round(loaf[zone] / max(1, sum(loaf.values())), 6),
            "favorite_zone_placement_share": round(placements[zone] / max(1, sum(placements.values())), 6),
            "favorite_object_nudge_share": round(nudges[object_id] / max(1, sum(nudges.values())), 6),
        }

    ap = patterns(ar1, "window", "amber_leaf")
    bp = patterns(br1, "activity_corner", "acorn")
    a_comfort = Counter(ap["comfort_counts"]); b_comfort = Counter(bp["comfort_counts"])
    a_loaf = Counter(ap["loaf_counts"]); b_loaf = Counter(bp["loaf_counts"])
    a_places = Counter(ap["placement_counts"]); b_places = Counter(bp["placement_counts"])
    comfort_total_a=max(1,sum(a_comfort.values())); comfort_total_b=max(1,sum(b_comfort.values()))
    loaf_total_a=max(1,sum(a_loaf.values())); loaf_total_b=max(1,sum(b_loaf.values()))
    place_total_a=max(1,sum(a_places.values())); place_total_b=max(1,sum(b_places.values()))
    comfort_cross = (a_comfort["window"]/comfort_total_a-b_comfort["window"]/comfort_total_b)+(b_comfort["activity_corner"]/comfort_total_b-a_comfort["activity_corner"]/comfort_total_a)
    loaf_cross = (a_loaf["window"]/loaf_total_a-b_loaf["window"]/loaf_total_b)+(b_loaf["activity_corner"]/loaf_total_b-a_loaf["activity_corner"]/loaf_total_a)
    placement_cross = (a_places["window"]/place_total_a-b_places["window"]/place_total_b)+(b_places["activity_corner"]/place_total_b-a_places["activity_corner"]/place_total_a)
    object_signature_a = [(o["id"], o["zone"], o["x"], o["y"], o.get("times_nudged",0)) for o in a1["objects"]]
    object_signature_b = [(o["id"], o["zone"], o["x"], o["y"], o.get("times_nudged",0)) for o in b1["objects"]]
    return {
        "steps": steps,
        "physical_state_equal_before_run": canonical_json(a_physical) == canonical_json(b_physical),
        "history_a_deterministic": canonical_json(a1) == canonical_json(a2) and ar1 == ar2,
        "history_b_deterministic": canonical_json(b1) == canonical_json(b2) and br1 == br2,
        "history_a": ap,
        "history_b": bp,
        "comfort_cross_advantage": round(comfort_cross, 6),
        "loaf_cross_advantage": round(loaf_cross, 6),
        "placement_cross_advantage": round(placement_cross, 6),
        "final_object_arrangements_diverge": object_signature_a != object_signature_b,
        "history_a_final_object_signature": object_signature_a,
        "history_b_final_object_signature": object_signature_b,
    }


def _baseline() -> dict[str, Any]:
    path = PROJECT_ROOT / "artifacts" / "pixel-art-overhaul-iteration6-baseline.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(steps: int = 10080, seeds: tuple[int, ...] = SEEDS) -> dict[str, Any]:
    baseline = _baseline()
    results: dict[str, Any] = {}
    for seed in seeds:
        final, rows = _run(seed, steps)
        summary = _summarize(final, rows)
        base = baseline["seeds"].get(str(seed), baseline["seeds"]["1701"])
        checks = {
            "all_meaningful_families_reached": set(summary["family_counts"]) == EXPECTED_FAMILIES,
            "new_actions_are_ordinary_but_bounded": set(summary["new_actions_seen"]) == NEW_ACTIONS and 0.10 <= summary["new_action_decision_share"] <= 0.28,
            "old_repertoire_remains_present": len(summary["old_actions_seen"]) == len(OLD_ACTIONS),
            "semantic_family_entropy_increased": summary["family_entropy_bits"] >= float(base["family_entropy_bits"]) + 0.18,
            "generic_behavior_share_reduced": summary["old_generic_decision_share"] <= float(base["old_generic_decision_share"]) - 0.06,
            "family_transition_space_expanded": summary["distinct_family_transitions"] >= 30,
            "zone_activity_space_is_broad": summary["distinct_zone_family_combinations"] >= 34,
            "repetition_stays_bounded": summary["max_non_sleep_family_streak"] <= 8,
            "no_family_dominates": summary["top_family_share"] <= 0.34,
            # 8D intentionally restricts nudge/play to the two rolling objects
            # plus the soft-nesting thread. Require consequences across every
            # eligible object instead of the pre-8D universal-object count.
            "object_manipulation_has_consequences": summary["objects_nudged"] >= 3 and summary["object_nudges"] >= 20 and summary["distinct_nudge_patterns"] >= 15,
            "arrangements_span_world": summary["zones_with_arrangement_history"] >= 4 and summary["distinct_arrangement_patterns"] >= 15,
            "comfort_spans_world": summary["zones_with_comfort_history"] == len(ZONES),
            "inspect_manipulate_sequences_are_common": summary["inspect_to_manipulation_within_two_rate"] >= 0.68,
            "nudge_has_causal_followup": summary["nudge_to_causal_followup_within_two_rate"] >= 0.70,
            "weather_reactions_have_followup": summary["weather_reactions"] >= 6 and summary["weather_reaction_to_window_within_two_rate"] >= 0.85,
        }
        results[str(seed)] = {"passed": all(checks.values()), "checks": checks, "metrics": summary}

    controlled = _history_divergence()
    controlled_checks = {
        "same_history_is_deterministic": controlled["history_a_deterministic"] and controlled["history_b_deterministic"],
        "controlled_worlds_start_physically_equal": controlled["physical_state_equal_before_run"],
        "histories_change_new_comfort_patterns": controlled["loaf_cross_advantage"] >= 0.18,
        "histories_change_arrangement_patterns": controlled["placement_cross_advantage"] >= 0.14,
        "histories_create_different_world_arrangements": controlled["final_object_arrangements_diverge"],
    }
    return {
        "schema": "terrarium.behavioral-repertoire-evaluation.v1",
        "steps_per_seed": steps,
        "seeds": list(seeds),
        "baseline": baseline,
        "results": results,
        "controlled_history_divergence": controlled,
        "controlled_checks": controlled_checks,
        "all_passed": all(item["passed"] for item in results.values()) and all(controlled_checks.values()),
    }


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--steps",type=int,default=10080); parser.add_argument("--out")
    args=parser.parse_args(); result=evaluate(args.steps)
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out: Path(args.out).write_text(text,encoding="utf-8")
    print(text,end="")
    return 0 if result["all_passed"] else 2

if __name__ == "__main__": raise SystemExit(main())
