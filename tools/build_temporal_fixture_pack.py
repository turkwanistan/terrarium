from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import Simulation
from terrarium.frame import make_frame
from terrarium.models import initial_state

SCHEMA = "terrarium.temporal-fixtures.v1"
CREATED_AT = "2026-01-01T00:00:00Z"


def _walk_scenarios(seed: int = 1701) -> dict[str, dict[str, Any]]:
    state = initial_state(seed, created_at=CREATED_AT)
    sim = Simulation()
    found: dict[str, dict[str, Any]] = {}
    for _ in range(800):
        before = state
        _, _, details, state = sim.step(state)
        old = before["creature"]
        new = state["creature"]
        if new["activity"] == "walk" and (new["x"] != old["x"] or new["y"] != old["y"]) and "arrive_settle" not in found:
            found["arrive_settle"] = _scenario("arrive_settle", before, state, details, "full semantic movement through endpoint settling")
        if new["activity"] == "walk" and new["x"] < old["x"] and "left_walk" not in found:
            found["left_walk"] = _scenario("left_walk", before, state, details, "semantic leftward walk")
        if new["activity"] == "walk" and new["x"] > old["x"] and "right_walk" not in found:
            found["right_walk"] = _scenario("right_walk", before, state, details, "semantic rightward walk")
        if old.get("carrying") and new["activity"] == "walk" and "carried_walk" not in found:
            found["carried_walk"] = _scenario("carried_walk", before, state, details, "semantic movement while carrying")
        if new["x"] == old["x"] and new["y"] == old["y"] and new["activity"] in {"idle", "rest", "inspect"} and "idle_control" not in found:
            found["idle_control"] = _scenario("idle_control", before, state, details, "no semantic translation; ambient motion allowed")
        if new["activity"] == "sleep" and new["zone"] == "sleeping_nook" and "sleep_transition" not in found:
            found["sleep_transition"] = _scenario("sleep_transition", before, state, details, "sleeping-nook contact and breathing transition")
        if new["activity"] == "look_outside" and new["zone"] == "window" and "window_transition" not in found:
            found["window_transition"] = _scenario("window_transition", before, state, details, "window-use contact transition")
        if new["zone"] == "activity_corner" and new["activity"] in {"inspect", "carry", "place"} and "activity_corner_transition" not in found:
            found["activity_corner_transition"] = _scenario("activity_corner_transition", before, state, details, "activity-corner surface interaction transition")
        if new["activity"] == "place" and "object_placement" not in found:
            found["object_placement"] = _scenario("object_placement", before, state, details, "carried object settles into its canonical authored placement")
        required={"arrive_settle", "left_walk", "right_walk", "carried_walk", "idle_control", "sleep_transition", "window_transition", "activity_corner_transition", "object_placement"}
        if required.issubset(found):
            break
    missing={"arrive_settle", "left_walk", "right_walk", "carried_walk", "idle_control", "sleep_transition", "window_transition", "activity_corner_transition", "object_placement"}-set(found)
    if missing:
        raise RuntimeError(f"missing deterministic scenarios: {sorted(missing)}")
    return found


def _rain_scenario() -> dict[str, Any]:
    state = initial_state(7, created_at=CREATED_AT)
    if state["habitat"]["weather"] != "rain":
        raise RuntimeError("seed 7 no longer starts in rain")
    # Ambient control intentionally uses identical semantic source/target frames.
    # Only explicit renderer time advances, so moving rain/dust is expected while
    # Moss remains semantically stationary.
    frame = make_frame(state)
    return {
        "id": "rain_control",
        "seed": 7,
        "source_tick": frame["tick"],
        "target_tick": frame["tick"],
        "source": frame,
        "target": deepcopy(frame),
        "semantic_event": {"action": "ambient_control", "from_zone": frame["creature"]["zone"], "to_zone": frame["creature"]["zone"]},
        "purpose": "rain/environmental animation control with no semantic translation",
    }


def _scenario(name: str, before: dict[str, Any], after: dict[str, Any], details: dict[str, Any], purpose: str) -> dict[str, Any]:
    source = make_frame(before)
    target = make_frame(after)
    return {
        "id": name,
        "seed": int(before["seed"]),
        "source_tick": source["tick"],
        "target_tick": target["tick"],
        "source": source,
        "target": target,
        "semantic_event": {
            "action": details.get("action"),
            "from_zone": details.get("from_zone"),
            "to_zone": details.get("to_zone", target["creature"]["zone"]),
        },
        "purpose": purpose,
    }


def build() -> dict[str, Any]:
    scenarios = _walk_scenarios()
    scenarios["rain_control"] = _rain_scenario()
    return {
        "schema": SCHEMA,
        "transition_duration_ms": 1500,
        "recommended_timestamps_ms": [0, 100, 250, 500, 750, 1000, 1250, 1400, 1500, 1650],
        "scenarios": scenarios,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/temporal-render-fixtures.json")
    args = parser.parse_args()
    payload = build()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "scenarios": sorted(payload["scenarios"]), "schema": payload["schema"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
