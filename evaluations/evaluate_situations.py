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
from terrarium.models import initial_state
from terrarium.situations import EVENT_CATALOG, SITUATIONAL_EVENTS_SCHEMA
from terrarium.spatial import point_is_walkable

FIXED = "2026-01-01T00:00:00Z"
SEEDS = (1701, 1702, 42, 999)
WINDOW_EVENTS = {"bird", "rain_intensify", "thunder", "leaf_tap"}
LOW_COMMITMENT_INTERRUPTIONS = {"idle", "rest", "loaf", "groom", "stretch"}


def _entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counter.values())


def _max_run(values: list[str]) -> int:
    best = run = 0
    current = None
    for value in values:
        if value == current:
            run += 1
        else:
            current, run = value, 1
        best = max(best, run)
    return best


def _run(seed: int, steps: int) -> dict[str, Any]:
    state = initial_state(seed, created_at=FIXED)
    sim = Simulation()
    starts: list[dict[str, Any]] = []
    ended: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    active_ticks = 0
    sunlight_checks: list[dict[str, Any]] = []
    for _ in range(steps):
        _, _, details, state = sim.step(state)
        active = (state["habitat"].get("situational_events") or {}).get("active")
        if active is not None:
            active_ticks += 1
        if details.get("world_event_started"):
            starts.append({"tick": int(state["tick"]), **deepcopy(details["world_event_started"])})
        if details.get("world_event_ended"):
            ended.append({"tick": int(state["tick"]), **deepcopy(details["world_event_ended"])})
        if details.get("decision"):
            row = {
                "tick": int(state["tick"]),
                "action": str(details.get("action") or ""),
                "family": str(details.get("activity_family") or Simulation._activity_family(str(details.get("action") or ""))),
                "zone": str(state["creature"]["zone"]),
                "x": int(state["creature"]["x"]),
                "y": int(state["creature"]["y"]),
                "world_event_id": details.get("world_event_id"),
                "world_event_type": details.get("world_event_type"),
                "world_event_role": details.get("world_event_role"),
                "attention_status": details.get("world_event_attention_status"),
                "supported_action": details.get("supported_action"),
                "interrupted_action": details.get("interrupted_action"),
                "target_x": details.get("target_x"),
                "target_y": details.get("target_y"),
            }
            decisions.append(row)
            if row["supported_action"] == "sunlight_affordance":
                sunlight_checks.append({
                    "event_active": bool(active and active.get("type") == "sunlight"),
                    "position_matches": bool(active and (row["x"], row["y"]) == (int(active["x"]), int(active["y"]))),
                    "walkable": point_is_walkable((row["x"], row["y"])),
                })
    return {"final": state, "starts": starts, "ended": ended, "decisions": decisions, "active_ticks": active_ticks, "sunlight_checks": sunlight_checks}


def _baseline(seed: int) -> dict[str, Any]:
    data = json.loads((PROJECT_ROOT / "artifacts" / "pixel-art-overhaul-iteration6-evaluation.json").read_text(encoding="utf-8"))
    return data["results"][str(seed)]["metrics"]


def _summarize(seed: int, steps: int, run: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    starts = run["starts"]
    ended = run["ended"]
    decisions = run["decisions"]
    start_counts = Counter(str(row["type"]) for row in starts)
    outcomes = Counter(str(row["outcome"]) for row in ended)
    response_steps = Counter(step for row in ended for step in row.get("response_path", []))
    linked = [row for row in decisions if row["world_event_id"]]
    action_counts = Counter(row["action"] for row in decisions)
    families = Counter(row["family"] for row in decisions)
    start_minutes = [int(row["start_world_minute"]) for row in starts]
    start_gaps = [b - a for a, b in zip(start_minutes, start_minutes[1:])]
    starts_by_type: dict[str, list[int]] = {}
    for row in starts:
        starts_by_type.setdefault(str(row["type"]), []).append(int(row["start_world_minute"]))
    same_type_gaps = [
        b - a for values in starts_by_type.values() for a, b in zip(values, values[1:])
    ]
    interruption_actions = Counter(str(row["interrupted_action"]) for row in decisions if row["interrupted_action"])

    by_event: dict[str, list[dict[str, Any]]] = {}
    for row in linked:
        by_event.setdefault(str(row["world_event_id"]), []).append(row)
    engaged = [row for row in ended if row["outcome"] == "engaged"]
    causal_ok = 0
    causal_bad: list[str] = []
    for event in engaged:
        rows = by_event.get(str(event["id"]), [])
        event_type = str(event["type"])
        if event_type == "sunlight":
            ok = any(row["supported_action"] == "sunlight_affordance" and row["action"] == "loaf" for row in rows)
        elif event_type == "moth":
            ok = any(row["world_event_role"] == "engage" and row["action"] == "react" and row["zone"] == "activity_corner" for row in rows)
        elif event_type in WINDOW_EVENTS:
            ok = any(row["world_event_role"] == "engage" and row["action"] == "look_outside" and row["zone"] == "window" for row in rows)
        else:
            ok = False
        if ok:
            causal_ok += 1
        else:
            causal_bad.append(str(event["id"]))

    baseline = _baseline(seed)
    generic_actions = {"idle", "rest", "walk", "explore", "sleep", "wake"}
    generic_share = sum(action_counts[name] for name in generic_actions) / max(1, len(decisions))
    linked_share = len(linked) / max(1, len(decisions))
    ordinary_share = 1.0 - linked_share
    metrics = {
        "events_started": len(starts),
        "events_ended": len(ended),
        "event_counts": dict(sorted(start_counts.items())),
        "event_active_timeline_share": round(run["active_ticks"] / max(1, steps), 6),
        "event_start_gap_minutes": {"min": min(start_gaps, default=0), "mean": round(sum(start_gaps) / max(1, len(start_gaps)), 6), "max": max(start_gaps, default=0)},
        "same_type_start_gap_minutes": {"min": min(same_type_gaps, default=0), "mean": round(sum(same_type_gaps) / max(1, len(same_type_gaps)), 6)},
        "outcome_counts": dict(sorted(outcomes.items())),
        "response_path_counts": dict(sorted(response_steps.items())),
        "event_linked_decision_share": round(linked_share, 6),
        "ordinary_autonomous_decision_share": round(ordinary_share, 6),
        "interruption_actions": dict(sorted(interruption_actions.items())),
        "engaged_events": len(engaged),
        "causal_engagements_verified": causal_ok,
        "causal_engagement_failures": causal_bad,
        "sunlight_affordance_uses": len(run["sunlight_checks"]),
        "sunlight_affordance_failures": sum(not all(item.values()) for item in run["sunlight_checks"]),
        "family_entropy_bits": round(_entropy(families), 6),
        "generic_decision_share": round(generic_share, 6),
        "iteration6_family_entropy_bits": float(baseline["family_entropy_bits"]),
        "iteration6_generic_decision_share": float(baseline["old_generic_decision_share"]),
        "action_counts": dict(sorted(action_counts.items())),
    }
    checks = {
        "all_authored_event_types_reachable": set(start_counts) == set(EVENT_CATALOG),
        "event_frequency_bounded": 40 <= len(starts) <= 90,
        "events_do_not_dominate_timeline": 0.04 <= metrics["event_active_timeline_share"] <= 0.14,
        "events_are_temporally_separated": metrics["event_start_gap_minutes"]["min"] >= 20,
        "same_event_clustering_bounded": metrics["same_type_start_gap_minutes"]["min"] >= 100,
        "response_diversity_includes_ignore_orient_engage": all(outcomes[name] > 0 for name in ("ignored", "oriented", "engaged")),
        "deferred_attention_is_exercised": response_steps["deferred"] > 0,
        "event_linked_behavior_is_bounded": metrics["event_linked_decision_share"] <= 0.12 and metrics["ordinary_autonomous_decision_share"] >= 0.88,
        "engagement_has_causal_followthrough": bool(engaged) and causal_ok == len(engaged),
        "sunlight_is_real_temporary_affordance": bool(run["sunlight_checks"]) and metrics["sunlight_affordance_failures"] == 0,
        "interruptions_only_break_low_commitment_actions": set(interruption_actions) <= LOW_COMMITMENT_INTERRUPTIONS,
        "iteration6_repertoire_not_crowded_out": metrics["family_entropy_bits"] >= float(baseline["family_entropy_bits"]) - 0.10 and metrics["generic_decision_share"] <= float(baseline["old_generic_decision_share"]) + 0.05,
    }
    return metrics, checks


def evaluate(steps: int = 10080, seeds: tuple[int, ...] = SEEDS) -> dict[str, Any]:
    results: dict[str, Any] = {}
    deterministic = True
    total_interruptions = 0
    for seed in seeds:
        first = _run(seed, steps)
        second = _run(seed, steps)
        deterministic = deterministic and first == second
        metrics, checks = _summarize(seed, steps, first)
        total_interruptions += sum(metrics["interruption_actions"].values())
        results[str(seed)] = {"passed": all(checks.values()), "checks": checks, "metrics": metrics}
    matrix_checks = {
        "same_seed_history_is_exactly_deterministic": deterministic,
        "rare_true_interruption_is_reachable_across_matrix": total_interruptions >= 1,
    }
    return {
        "schema": "terrarium.situational-events-evaluation.v1",
        "situational_events_schema": SITUATIONAL_EVENTS_SCHEMA,
        "steps_per_seed": steps,
        "seeds": list(seeds),
        "results": results,
        "matrix_checks": matrix_checks,
        "all_passed": all(item["passed"] for item in results.values()) and all(matrix_checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10080)
    parser.add_argument("--out")
    args = parser.parse_args()
    result = evaluate(args.steps)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["all_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
