from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_temporal_fixture_pack import build as build_temporal_pack

SCHEMA = "terrarium.godot-fixtures.v1"


def _environment_clone(frame: dict, *, season_frame: dict, weather: str, lighting: str) -> dict:
    result = deepcopy(frame)
    result["weather"] = weather
    result["lighting"] = lighting
    result["season"] = deepcopy(season_frame["season"])
    result["last_event"] = {
        "event_id": "fixture-godot-environment",
        "type": "fixture",
        "summary": "Fixture-backed Godot presentation environment control.",
        "action": "ambient_control",
        "object_id": None,
        "from_zone": result["creature"]["zone"],
        "to_zone": result["creature"]["zone"],
        "decision": False,
        "intent_action": "ambient_control",
        "target_x": None,
        "target_y": None,
        "contact_x": None,
        "contact_y": None,
        "spatial_schema": None,
        "source_x": None,
        "source_y": None,
        "approach_x": None,
        "approach_y": None,
        "route_length": None,
        "route": [],
        "supported_action": None,
        "activity_family": None,
        "result_x": None,
        "result_y": None,
        "object_affordance_schema": None,
        "object_archetype": None,
        "object_affordance": None,
        "object_state_before": None,
        "object_state_after": None,
        "world_event_id": None,
        "world_event_type": None,
        "world_event_role": None,
        "world_event_attention_status": None,
        "world_event_started": None,
        "world_event_ended": None,
    }
    return result


def build() -> dict:
    source = build_temporal_pack()
    scenarios = source["scenarios"]
    idle = deepcopy(scenarios["inspect_object"]["source"])
    spring = scenarios["season_spring_day"]["target"]
    winter = scenarios["season_winter_warm_night"]
    clear_idle = _environment_clone(idle, season_frame=spring, weather="clear", lighting="day")
    rain_idle = _environment_clone(idle, season_frame=spring, weather="rain", lighting="day")
    result = {
        "schema": SCHEMA,
        "frame_schema": "terrarium.frame.v1",
        "art_surface": [400, 240],
        "semantic_frame": [800, 480],
        "transition_duration_ms": source["transition_duration_ms"],
        "scenarios": {
            "spring_clear_idle": {"source": deepcopy(clear_idle), "target": deepcopy(clear_idle), "purpose": "idle Moss in sleeping-nook slice on a spring clear day"},
            "spring_rain_idle": {"source": deepcopy(rain_idle), "target": deepcopy(rain_idle), "purpose": "same canonical fixture position under authoritative rain"},
            "winter_warm_night": deepcopy(winter),
            "walk_to_window": deepcopy(scenarios["left_walk"]),
            "inspect_red_thread": deepcopy(scenarios["inspect_object"]),
            "pickup_red_thread": deepcopy(scenarios["object_pickup"]),
            "carry_walk": deepcopy(scenarios["carried_walk"]),
            "red_thread_rumpled": deepcopy(scenarios["object_tug"]),
            "red_thread_nested": deepcopy(scenarios["object_nest"]),
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="display/godot/tests/fixtures/vertical_slice.json")
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
