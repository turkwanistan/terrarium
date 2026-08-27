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
    required = {
        "arrive_settle", "left_walk", "right_walk", "carried_walk", "idle_control",
        "sleep_transition", "waking", "window_transition", "activity_corner_transition",
        "inspect_object", "object_pickup", "object_placement",
    }
    for _ in range(1200):
        before = state
        _, _, details, state = sim.step(state)
        old = before["creature"]
        new = state["creature"]
        moved = new["x"] != old["x"] or new["y"] != old["y"]
        if new["activity"] == "walk" and moved and "arrive_settle" not in found:
            found["arrive_settle"] = _scenario("arrive_settle", before, state, details, "full semantic movement through endpoint settling")
        if new["activity"] == "walk" and new["x"] < old["x"] and "left_walk" not in found:
            found["left_walk"] = _scenario("left_walk", before, state, details, "semantic leftward walk")
        if new["activity"] == "walk" and new["x"] > old["x"] and "right_walk" not in found:
            found["right_walk"] = _scenario("right_walk", before, state, details, "semantic rightward walk")
        if old.get("carrying") and new["activity"] == "walk" and "carried_walk" not in found:
            found["carried_walk"] = _scenario("carried_walk", before, state, details, "semantic movement while carrying")
        if not moved and new["activity"] in {"idle", "rest"} and "idle_control" not in found:
            found["idle_control"] = _scenario("idle_control", before, state, details, "quiet no-translation control with restrained idle motion")
        if new["activity"] == "sleep" and new["zone"] == "sleeping_nook" and "sleep_transition" not in found:
            found["sleep_transition"] = _scenario("sleep_transition", before, state, details, "sleeping-nook contact and curl/settle transition")
        if details.get("action") == "wake" and "waking" not in found:
            found["waking"] = _scenario("waking", before, state, details, "deliberate wake/recovery from sleep")
        if new["activity"] == "look_outside" and new["zone"] == "window" and "window_transition" not in found:
            found["window_transition"] = _scenario("window_transition", before, state, details, "window-use settle and observation transition")
        if new["zone"] == "activity_corner" and new["activity"] in {"inspect", "carry", "place"} and "activity_corner_transition" not in found:
            found["activity_corner_transition"] = _scenario("activity_corner_transition", before, state, details, "activity-corner surface interaction transition")
        if details.get("action") == "inspect" and details.get("object_id") and "inspect_object" not in found:
            found["inspect_object"] = _scenario("inspect_object", before, state, details, "targeted object inspection with face/lean/contact staging")
        if details.get("action") == "carry" and details.get("object_id") and not old.get("carrying") and "object_pickup" not in found:
            found["object_pickup"] = _scenario("object_pickup", before, state, details, "object reach/contact/attachment transition")
        if new["activity"] == "place" and "object_placement" not in found:
            found["object_placement"] = _scenario("object_placement", before, state, details, "carried object lowers and settles into its canonical authored placement")
        if required.issubset(found):
            break
    missing = required - set(found)
    if missing:
        raise RuntimeError(f"missing deterministic scenarios: {sorted(missing)}")
    return found


def _rain_scenario() -> dict[str, Any]:
    state = initial_state(7, created_at=CREATED_AT)
    if state["habitat"]["weather"] != "rain":
        raise RuntimeError("seed 7 no longer starts in rain")
    frame = make_frame(state)
    return {
        "id": "rain_control",
        "seed": 7,
        "source_tick": frame["tick"],
        "target_tick": frame["tick"],
        "source": frame,
        "target": deepcopy(frame),
        "semantic_event": {"action": "ambient_control", "from_zone": frame["creature"]["zone"], "to_zone": frame["creature"]["zone"]},
        "purpose": "restrained rain/environmental animation control with no semantic translation",
    }


def _rain_window_scenario() -> dict[str, Any]:
    state = initial_state(1, created_at=CREATED_AT)
    sim = Simulation()
    for _ in range(500):
        before = state
        _, _, details, state = sim.step(state)
        if details.get("action") == "look_outside" and details.get("weather") == "rain" and state["creature"]["zone"] == "window":
            return _scenario("rain_window", before, state, details, "Moss calmly watches rain from the sill-side contact point")
    raise RuntimeError("unable to build deterministic rain_window scenario")


def _populated_room_scenario(seed: int = 1701, steps: int = 240) -> dict[str, Any]:
    state = initial_state(seed, created_at=CREATED_AT)
    sim = Simulation()
    details: dict[str, Any] = {}
    for _ in range(steps):
        _, _, details, state = sim.step(state)
    frame = make_frame(state, last_event={
        "event_id": "fixture-populated-room",
        "type": "fixture",
        "summary": "Deterministic lived-in room control.",
        "details": details,
    })
    return {
        "id": "populated_room",
        "seed": seed,
        "source_tick": frame["tick"],
        "target_tick": frame["tick"],
        "source": frame,
        "target": deepcopy(frame),
        "semantic_event": {"action": "lived_in_control", "from_zone": frame["creature"]["zone"], "to_zone": frame["creature"]["zone"]},
        "purpose": "populated/lived-in composition control after deterministic accumulated history",
    }


def _scenario(name: str, before: dict[str, Any], after: dict[str, Any], details: dict[str, Any], purpose: str) -> dict[str, Any]:
    source = make_frame(before)
    target = make_frame(after, last_event={
        "event_id": f"fixture-{name}",
        "type": "fixture",
        "summary": purpose,
        "details": details,
    })
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
            "object_id": details.get("object_id"),
        },
        "purpose": purpose,
    }



def _continuity_probe(seed: int = 1701) -> dict[str, Any]:
    state = initial_state(seed, created_at=CREATED_AT)
    sim = Simulation()
    prior: dict[str, Any] | None = None
    movement = {"walk", "explore"}
    for _ in range(1200):
        before = state
        _, _, details, state = sim.step(state)
        if details.get("action") in movement and prior and prior["details"].get("action") in movement:
            middle = make_frame(before, last_event={
                "event_id": "fixture-continuity-middle",
                "type": "fixture",
                "summary": "First movement in a consecutive canonical update chain.",
                "details": prior["details"],
            })
            followup = make_frame(state, last_event={
                "event_id": "fixture-continuity-followup",
                "type": "fixture",
                "summary": "Second movement in a consecutive canonical update chain.",
                "details": details,
            })
            return {
                "id": "continuity_probe",
                "seed": seed,
                "source": make_frame(prior["before"]),
                "middle": middle,
                "followup": followup,
                "first_event": prior["details"],
                "second_event": details,
                "interrupt_ms": 1000,
                "purpose": "measure renderer discontinuity when a new canonical tick arrives before the prior visual transition finishes",
            }
        prior = {"before": before, "details": details} if details.get("action") in movement else None
    raise RuntimeError("unable to build deterministic continuity probe")

def build() -> dict[str, Any]:
    scenarios = _walk_scenarios()
    scenarios["rain_window"] = _rain_window_scenario()
    scenarios["populated_room"] = _populated_room_scenario()
    scenarios["rain_control"] = _rain_scenario()
    hero_reel = [
        "left_walk", "right_walk", "arrive_settle", "idle_control", "window_transition",
        "rain_window", "inspect_object", "object_pickup", "carried_walk", "object_placement",
        "sleep_transition", "waking", "activity_corner_transition", "populated_room", "rain_control",
    ]
    return {
        "schema": SCHEMA,
        "transition_duration_ms": 2600,
        "recommended_timestamps_ms": [0, 100, 250, 500, 800, 1100, 1400, 1700, 2000, 2300, 2600],
        "hero_reel": hero_reel,
        "continuity_probe": _continuity_probe(),
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
