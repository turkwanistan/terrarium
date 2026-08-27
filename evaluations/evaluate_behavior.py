#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import WorldEngine
from terrarium.store import WorldStore


def entropy(values: list[str]) -> float:
    counts = collections.Counter(values)
    n = len(values)
    return 0.0 if not n else -sum((c/n) * math.log2(c/n) for c in counts.values())


def max_run(values: list[str]) -> tuple[str | None, int]:
    best = (None, 0); current = None; run = 0
    for value in values:
        if value == current:
            run += 1
        else:
            if run > best[1]: best = (current, run)
            current, run = value, 1
    return (current, run) if run > best[1] else best


def evaluate(seed: int, steps: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="terrarium-behavior-") as tmp:
        store = WorldStore(tmp)
        store.initialize(seed, created_at="2026-01-01T00:00:00Z")
        engine = WorldEngine(store, seed=seed)
        events = engine.run_steps(steps)
        timeline_actions = [e["details"]["action"] for e in events]
        decision_events = [e for e in events if e["details"].get("decision", True)]
        actions = [e["details"].get("intent_action", e["details"]["action"]) for e in decision_events]
        counts = collections.Counter(actions)
        timeline_counts = collections.Counter(timeline_actions)
        run_action, run_length = max_run(timeline_actions)
        object_placements = sum(e["type"] == "object_placed" for e in events)
        object_inspections = sum(e["type"] == "object_inspected" for e in events)
        object_pickups = sum(e["type"] == "object_picked_up" for e in events)
        moved_objects = sum(int(o["times_moved"]) > 0 for o in engine.state["objects"])
        marks = len(engine.state["habitat"]["marks"])
        shelf = int(engine.state["habitat"]["shelf_count"])
        affordance = engine.state["habitat"].get("affordance_history") or {}
        object_nudges = sum(int(o.get("times_nudged", 0)) for o in engine.state["objects"])
        arrangement_places = int((engine.state["habitat"].get("activity_aftermath") or {}).get("arrangement_places", 0))
        presentation = _presentation_metrics(decision_events)
        visible_intent_changes = sum(1 for i in range(1, len(timeline_actions)) if timeline_actions[i] != timeline_actions[i-1])
        checks = {
            "action_diversity": len(counts) >= 8,
            "non_sleep_repeat_run_bounded": max((n for a,n in _runs(actions) if a != "sleep"), default=0) <= 4,
            "movement_commitment_bounded": presentation["max_consecutive_movement_actions"] <= 3,
            "immediate_zone_reversals_bounded": presentation["immediate_zone_reversals"] <= max(2, steps // 75),
            "object_manipulation_burst_bounded": presentation["max_consecutive_object_manipulations"] <= 3,
            "object_interaction_present": object_placements >= max(2, len(decision_events) // 20),
            "multiple_objects_changed": moved_objects >= 3,
            "visible_environment_accumulated": (
                marks >= max(1, len(decision_events) // 80) or shelf >= 2 or object_nudges >= 1 or arrangement_places >= 2
            ),
            "no_impossible_carry_state": _carry_consistent(engine.state),
        }
        result = {
            "schema": "terrarium.behavior-evaluation.v1",
            "seed": seed,
            "steps": steps,
            "passed": all(checks.values()),
            "checks": checks,
            "metrics": {
                "action_counts": dict(sorted(counts.items())),
                "timeline_action_counts": dict(sorted(timeline_counts.items())),
                "decision_events": len(decision_events),
                "continuation_events": len(events) - len(decision_events),
                "visible_intent_changes": visible_intent_changes,
                "action_diversity": len(counts),
                "action_entropy_bits": round(entropy(actions), 6),
                "timeline_action_entropy_bits": round(entropy(timeline_actions), 6),
                "max_repeat_run": {"action": run_action, "length": run_length},
                "object_placements": object_placements,
                "object_pickups": object_pickups,
                "object_inspections": object_inspections,
                "moved_objects": moved_objects,
                "shelf_count": shelf,
                "persistent_marks": marks,
                "object_nudges": object_nudges,
                "arrangement_places": arrangement_places,
                "affordance_families_recorded": len((affordance.get("completed_families") or {})),
                "events": len(events),
                **presentation,
            },
        }
        store.close()
        return result



def _presentation_metrics(events: list[dict]) -> dict:
    movement = {"walk", "explore"}
    manipulation = {"carry", "place", "nudge"}
    move_pairs = reversals = adjacent_manip = 0
    move_run = manip_run = max_move = max_manip = 0
    for i, event in enumerate(events):
        details = event["details"]
        action = details["action"]
        if action in movement:
            move_run += 1
            max_move = max(max_move, move_run)
        else:
            move_run = 0
        if action in manipulation:
            manip_run += 1
            max_manip = max(max_manip, manip_run)
        else:
            manip_run = 0
        if i:
            prior = events[i - 1]["details"]
            if prior["action"] in movement and action in movement:
                move_pairs += 1
                prior_to = prior.get("to_zone", prior.get("from_zone"))
                current_to = details.get("to_zone", details.get("from_zone"))
                if prior.get("from_zone") == current_to and prior_to == details.get("from_zone"):
                    reversals += 1
            if prior["action"] in manipulation and action in manipulation:
                adjacent_manip += 1
    return {
        "consecutive_movement_pairs": move_pairs,
        "immediate_zone_reversals": reversals,
        "max_consecutive_movement_actions": max_move,
        "adjacent_object_manipulation_pairs": adjacent_manip,
        "max_consecutive_object_manipulations": max_manip,
    }

def _runs(values):
    current=None; n=0
    for value in values:
        if value==current: n+=1
        else:
            if current is not None: yield current,n
            current,n=value,1
    if current is not None: yield current,n


def _carry_consistent(state: dict) -> bool:
    carrying = state["creature"]["carrying"]
    carried = [o for o in state["objects"] if o["state"] == "carried"]
    if carrying is None:
        return not carried
    return len(carried) == 1 and carried[0]["id"] == carrying and carried[0]["carried_by"] == state["creature"]["id"]


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--seed",type=int,default=1701); p.add_argument("--steps",type=int,default=240); p.add_argument("--out")
    args=p.parse_args(); result=evaluate(args.seed,args.steps)
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out: Path(args.out).write_text(text)
    print(text,end="")
    return 0 if result["passed"] else 2

if __name__ == "__main__": raise SystemExit(main())
