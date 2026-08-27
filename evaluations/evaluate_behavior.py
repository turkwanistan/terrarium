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
        actions = [e["details"]["action"] for e in events]
        counts = collections.Counter(actions)
        run_action, run_length = max_run(actions)
        object_placements = sum(e["type"] == "object_placed" for e in events)
        object_inspections = sum(e["type"] == "object_inspected" for e in events)
        object_pickups = sum(e["type"] == "object_picked_up" for e in events)
        moved_objects = sum(int(o["times_moved"]) > 0 for o in engine.state["objects"])
        marks = len(engine.state["habitat"]["marks"])
        shelf = int(engine.state["habitat"]["shelf_count"])
        checks = {
            "action_diversity": len(counts) >= 8,
            "non_sleep_repeat_run_bounded": max((n for a,n in _runs(actions) if a != "sleep"), default=0) <= 4,
            "object_interaction_present": object_placements >= max(2, steps // 40),
            "multiple_objects_changed": moved_objects >= 3,
            "visible_environment_accumulated": marks >= 3 or shelf >= 2,
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
                "action_diversity": len(counts),
                "action_entropy_bits": round(entropy(actions), 6),
                "max_repeat_run": {"action": run_action, "length": run_length},
                "object_placements": object_placements,
                "object_pickups": object_pickups,
                "object_inspections": object_inspections,
                "moved_objects": moved_objects,
                "shelf_count": shelf,
                "persistent_marks": marks,
                "events": len(events),
            },
        }
        store.close()
        return result


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
