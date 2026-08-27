#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import Simulation
from terrarium.models import canonical_json, initial_state
from terrarium.spatial import FAVORITE_SPOTS, point_is_walkable

FIXED = "2026-01-01T00:00:00Z"
MOVEMENT = {"walk", "explore"}
LOCAL_SETTLE = {"idle", "rest", "loaf", "groom", "stretch"}
OBJECT_ACTIONS = {"inspect", "nudge", "carry", "place"}


def _run(seed: int, steps: int) -> tuple[dict, list[dict]]:
    state = initial_state(seed, created_at=FIXED)
    sim = Simulation()
    rows: list[dict] = []
    for tick in range(1, steps + 1):
        _, _, details, state = sim.step(state)
        context = deepcopy(state["creature"].get("behavior_context") or {})
        rows.append(
            {
                "tick": tick,
                "decision": bool(details.get("decision", True)),
                "action": details.get("intent_action", details.get("action")),
                "visible": details.get("action"),
                "from_zone": details.get("from_zone"),
                "to_zone": details.get("to_zone"),
                "zone": state["creature"]["zone"],
                "object_id": details.get("object_id"),
                "travel_purpose": details.get("travel_purpose"),
                "delivery_target_zone": details.get("delivery_target_zone"),
                "route_length": float(details.get("route_length", 0.0) or 0.0),
                "placed_objects_in_zone": sorted(
                    str(obj["id"])
                    for obj in state["objects"]
                    if obj["state"] == "placed" and obj["zone"] == state["creature"]["zone"]
                ),
                "context": context,
            }
        )
    return state, rows


def _rate(numerator: int, denominator: int) -> float:
    return 0.0 if denominator <= 0 else numerator / denominator


def evaluate(seed: int, steps: int) -> dict:
    final, rows = _run(seed, steps)
    final2, rows2 = _run(seed, steps)
    decisions = [row for row in rows if row["decision"]]
    movement = [row for row in decisions if row["action"] in MOVEMENT]
    non_delivery = [row for row in movement if row["travel_purpose"] != "object_delivery"]

    zone_segments: list[tuple[str, int]] = []
    if rows:
        current_zone = str(rows[0]["zone"])
        start_tick = 1
        for row in rows[1:]:
            zone = str(row["zone"])
            if zone != current_zone:
                zone_segments.append((current_zone, int(row["tick"]) - start_tick))
                current_zone = zone
                start_tick = int(row["tick"])
        zone_segments.append((current_zone, steps + 1 - start_tick))
    dwell_values = [duration for _, duration in zone_segments]

    arrivals = [(i, row) for i, row in enumerate(decisions[:-1]) if row["action"] in MOVEMENT]
    post_arrival_lingers = sum(
        decisions[i + 1]["action"] not in MOVEMENT and decisions[i + 1]["from_zone"] == row["to_zone"]
        for i, row in arrivals
    )

    non_delivery_reversals = sum(
        prior["from_zone"] == current["to_zone"] and prior["to_zone"] == current["from_zone"]
        for prior, current in zip(non_delivery, non_delivery[1:])
    )

    inspect_sessions = [(i, row) for i, row in enumerate(decisions) if row["action"] == "inspect" and row["object_id"]]
    inspect_continuations = 0
    for i, row in inspect_sessions:
        if any(
            candidate["action"] in {"carry", "nudge"} and candidate["object_id"] == row["object_id"]
            for candidate in decisions[i + 1 : i + 3]
        ):
            inspect_continuations += 1

    window_arrivals = [(i, row) for i, row in enumerate(decisions) if row["travel_purpose"] == "window_session"]
    window_continuations = sum(
        any(candidate["action"] == "look_outside" and candidate["from_zone"] == "window" for candidate in decisions[i + 1 : i + 3])
        for i, _ in window_arrivals
    )

    places = [(i, row) for i, row in enumerate(decisions[:-1]) if row["action"] == "place"]
    post_place_lingers = sum(
        decisions[i + 1]["action"] not in MOVEMENT and decisions[i + 1]["from_zone"] == row["from_zone"]
        for i, row in places
    )

    wakes = [(i, row) for i, row in enumerate(decisions[:-1]) if row["action"] == "wake"]
    wake_recoveries = sum(decisions[i + 1]["action"] in LOCAL_SETTLE for i, _ in wakes)

    deliveries = [(i, row) for i, row in enumerate(decisions) if row["action"] == "carry" and row["delivery_target_zone"]]
    direct_deliveries = 0
    for i, pickup in deliveries:
        continuation = next(
            (candidate for candidate in decisions[i + 1 :] if candidate["action"] in MOVEMENT | {"place", "carry"}),
            None,
        )
        if continuation is None:
            continue
        if continuation["action"] == "place":
            direct_deliveries += continuation["from_zone"] == pickup["delivery_target_zone"]
        elif continuation["action"] in MOVEMENT:
            direct_deliveries += continuation["to_zone"] == pickup["delivery_target_zone"]

    post_place_object_repeats = 0
    post_place_object_samples = 0
    for i, placed in [(i, row) for i, row in enumerate(decisions) if row["action"] == "place" and row["object_id"]]:
        # Only judge fixation when Moss actually has another local object choice.
        # If a zone contains one object, returning attention to it is not repetition
        # caused by bad selection logic. Stop the sample when Moss leaves the zone.
        if len(placed["placed_objects_in_zone"]) < 2:
            continue
        nxt = None
        for candidate in decisions[i + 1 :]:
            if candidate["action"] in MOVEMENT:
                break
            if candidate["action"] in {"inspect", "carry"} and candidate["object_id"]:
                nxt = candidate
                break
        if nxt is not None:
            post_place_object_samples += 1
            post_place_object_repeats += nxt["object_id"] == placed["object_id"]

    context_bounded = all(
        len((row["context"] or {}).get("recent_zones", [])) <= 4
        and len((row["context"] or {}).get("recent_objects", [])) <= 4
        for row in rows
    )
    favorite_spots_walkable = all(
        point_is_walkable((int(spot["x"]), int(spot["y"]))) for spot in FAVORITE_SPOTS.values()
    )
    long_moves = sum(row["route_length"] >= 300.0 for row in movement)
    simulated_hours = max(steps / 60.0, 1e-9)
    calm_visible = sum(row["visible"] in {"idle", "rest", "loaf", "groom", "stretch", "sleep", "look_outside"} for row in rows)

    metrics = {
        "decision_events": len(decisions),
        "continuation_events": steps - len(decisions),
        "decisions_per_simulated_hour": round(len(decisions) / simulated_hours, 6),
        "movement_decisions": len(movement),
        "movement_decision_ratio": round(_rate(len(movement), len(decisions)), 6),
        "moves_per_simulated_hour": round(len(movement) / simulated_hours, 6),
        "cross_room_moves_per_simulated_hour": round(long_moves / simulated_hours, 6),
        "purposeful_movement_rate": round(_rate(sum(bool(row["travel_purpose"]) for row in movement), len(movement)), 6),
        "non_delivery_reversals": non_delivery_reversals,
        "non_delivery_reversal_rate": round(_rate(non_delivery_reversals, len(non_delivery) - 1), 6),
        "post_arrival_linger_rate": round(_rate(post_arrival_lingers, len(arrivals)), 6),
        "inspect_to_same_object_followup_within_two_decisions_rate": round(_rate(inspect_continuations, len(inspect_sessions)), 6),
        "window_session_continuation_rate": round(_rate(window_continuations, len(window_arrivals)), 6),
        "post_place_linger_rate": round(_rate(post_place_lingers, len(places)), 6),
        "wake_recovery_rate": round(_rate(wake_recoveries, len(wakes)), 6),
        "direct_object_delivery_rate": round(_rate(direct_deliveries, len(deliveries)), 6),
        "post_place_next_object_repeat_rate": round(_rate(post_place_object_repeats, post_place_object_samples), 6),
        "average_zone_dwell_ticks": round(statistics.mean(dwell_values), 6) if dwell_values else 0.0,
        "median_zone_dwell_ticks": statistics.median(dwell_values) if dwell_values else 0.0,
        "calm_visible_timeline_ratio": round(_rate(calm_visible, steps), 6),
        "decision_action_counts": dict(sorted(Counter(str(row["action"]) for row in decisions).items())),
        "travel_purpose_counts": dict(sorted(Counter(str(row["travel_purpose"]) for row in movement).items())),
    }
    checks = {
        "deterministic_execution": rows == rows2 and canonical_json(final) == canonical_json(final2),
        "bounded_routine_context": context_bounded,
        "favorite_spots_are_physically_valid": favorite_spots_walkable,
        "movement_is_mostly_consequence_not_default": metrics["movement_decision_ratio"] <= 0.21,
        "cross_room_motion_is_bounded": metrics["cross_room_moves_per_simulated_hour"] <= 1.9,
        "movement_has_readable_purpose": metrics["purposeful_movement_rate"] >= 0.95,
        "non_delivery_ping_pong_is_rare": metrics["non_delivery_reversal_rate"] <= 0.08,
        "arrivals_usually_linger": metrics["post_arrival_linger_rate"] >= 0.93,
        "object_inspection_often_continues": metrics["inspect_to_same_object_followup_within_two_decisions_rate"] >= 0.70,
        "window_arrivals_become_sessions": metrics["window_session_continuation_rate"] >= 0.80,
        "placed_objects_get_settle_time": metrics["post_place_linger_rate"] >= 0.90,
        "wake_has_recovery_before_travel": metrics["wake_recovery_rate"] >= 0.90,
        "object_delivery_follows_chosen_intent": metrics["direct_object_delivery_rate"] >= 0.95,
        "recent_object_inhibition_prevents_fixation": metrics["post_place_next_object_repeat_rate"] <= 0.35,
        "zone_dwell_is_meaningful": metrics["average_zone_dwell_ticks"] >= 12.0 and metrics["median_zone_dwell_ticks"] >= 10.0,
        "calm_behavior_dominates_timeline": metrics["calm_visible_timeline_ratio"] >= 0.65,
    }
    return {
        "schema": "terrarium.behavior-coherence-evaluation.v1",
        "seed": seed,
        "steps": steps,
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--steps", type=int, default=2000)
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
