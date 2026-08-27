#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrarium.engine import WorldEngine
from terrarium.frame import make_frame
from terrarium.models import PLACEMENT_SLOTS
from terrarium.store import WorldStore

DEFAULT_BASELINE = ROOT / "snapshots" / "dev" / "20260827T041252779231Z-gen17-accepted-baseline" / "frame.json"


def deterministic_frame(seed: int, steps: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="terrarium-storytelling-") as tmp:
        store = WorldStore(tmp)
        store.initialize(seed, created_at="2026-01-01T00:00:00Z")
        engine = WorldEngine(store, seed=seed)
        engine.run_steps(steps)
        frame = make_frame(engine.current_state(), last_event=store.last_event())
        store.close()
        return frame


def metrics(frame: dict) -> dict:
    wear = frame.get("habitat", {}).get("path_wear") or {}
    placed = [obj for obj in frame.get("objects", []) if obj.get("state") == "placed"]
    intentional = [
        obj
        for obj in placed
        if tuple((obj.get("x"), obj.get("y"))) in PLACEMENT_SLOTS.get(str(obj.get("zone")), [])
    ]
    moved = [obj for obj in frame.get("objects", []) if int(obj.get("times_moved", 0)) > 0]
    settled = [obj for obj in placed if int(obj.get("times_moved", 0)) >= 2]
    return {
        "tick": int(frame["tick"]),
        "placed_objects": len(placed),
        "objects_moved": len(moved),
        "total_object_moves": sum(int(obj.get("times_moved", 0)) for obj in frame.get("objects", [])),
        "intentional_anchor_objects": len(intentional),
        "intentional_anchor_ratio": round(len(intentional) / len(placed), 3) if placed else 0.0,
        "settled_objects_with_scuff_cue": len(settled),
        "total_path_wear": sum(int(value) for value in wear.values()),
        "visible_route_count": sum(int(value) >= 5 for value in wear.values() if value is not None),
        "strong_route_count": sum(int(value) >= 25 for value in wear.values() if value is not None),
        "persistent_mark_count": len(frame.get("habitat", {}).get("marks") or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare objective visual-storytelling cues across Terrarium life stages.")
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--improved-steps", type=int, default=720)
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument("--out")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = ROOT / baseline_path
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    fresh = deterministic_frame(args.seed, 0)
    improved = deterministic_frame(args.seed, args.improved_steps)

    result = {
        "schema": "terrarium.visual-storytelling-comparison.v1",
        "note": "Objective diorama cues only; this does not claim to be a subjective visual-quality oracle.",
        "seed": args.seed,
        "baseline_frame": str(baseline_path.relative_to(ROOT)),
        "fresh": metrics(fresh),
        "gen17_baseline": metrics(baseline),
        "improved_accelerated_life": metrics(improved),
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
