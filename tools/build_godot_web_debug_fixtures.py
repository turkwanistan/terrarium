from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_godot_vertical_slice_fixtures import build as build_godot_pack
from tools.build_temporal_fixture_pack import build as build_temporal_pack

SCHEMA = "terrarium.godot-web-debug-fixtures.v1"


def _retick(frame: dict, tick: int, *, activity: str | None = None, pose: str | None = None) -> dict:
    result = deepcopy(frame)
    result["tick"] = tick
    result["world_minutes"] = int(result.get("world_minutes", 0)) + tick
    creature = result["creature"]
    if activity is not None:
        creature["activity"] = activity
    if pose is not None:
        creature["pose"] = pose
    event = result.get("last_event")
    if isinstance(event, dict):
        event["event_id"] = f"fixture-web-{tick:04d}"
    return result


def _hold(sequence: list[dict], frame: dict, next_tick: int, count: int) -> int:
    for _ in range(count):
        sequence.append(_retick(frame, next_tick))
        next_tick += 1
    return next_tick


def build() -> dict:
    temporal = build_temporal_pack()["scenarios"]
    godot = build_godot_pack()["scenarios"]
    sequence: list[dict] = []
    tick = 1000

    idle = _retick(godot["spring_clear_idle"]["target"], tick, activity="idle", pose="idle")
    idle["creature"]["carrying"] = None
    sequence.append(idle)
    tick += 1

    # Route fixture with a real canonical multi-segment route. At the browser gate's 300 ms
    # debug poll, the next frames arrive before the 450 ms minimum transition finishes, forcing
    # the Web runtime to exercise rendered-position rebasing instead of only settled arrivals.
    walk = _retick(temporal["left_walk"]["target"], tick)
    sequence.append(walk)
    sequence.append(deepcopy(walk))  # duplicate tick must be ignored by the adapter
    older = _retick(walk, tick - 1)
    sequence.append(older)  # older tick must also be ignored
    tick += 1
    tick = _hold(sequence, walk, tick, 4)

    # A second route/corner while the first visual transition can still be in flight.
    walk_back = _retick(temporal["right_walk"]["target"], tick)
    walk_back["creature"]["carrying"] = None
    sequence.append(walk_back)
    tick += 1
    tick = _hold(sequence, walk_back, tick, 3)

    action_holds = [
        ("inspect", temporal["inspect_object"]["target"], 6),
        ("nudge", temporal["object_nudge"]["target"], 8),
        ("groom", temporal["groom"]["target"], 9),
        ("stretch", temporal["stretch"]["target"], 8),
        ("loaf", temporal["loaf"]["target"], 4),
        ("rest", temporal["season_winter_warm_night"]["target"], 4),
        ("react", temporal["event_thunder_react"]["target"], 5),
        ("look_outside", temporal["rain_window"]["target"], 6),
    ]
    for _name, template, count in action_holds:
        first = _retick(template, tick)
        sequence.append(first)
        tick += 1
        tick = _hold(sequence, first, tick, count - 1)

    pickup = _retick(temporal["object_pickup"]["target"], tick)
    sequence.append(pickup)
    tick += 1
    tick = _hold(sequence, pickup, tick, 6)

    carried_walk = _retick(temporal["carried_walk"]["target"], tick)
    sequence.append(carried_walk)
    tick += 1
    tick = _hold(sequence, carried_walk, tick, 4)

    place = _retick(temporal["object_placement"]["target"], tick)
    sequence.append(place)
    tick += 1
    tick = _hold(sequence, place, tick, 6)

    sleep = _retick(temporal["sleep_transition"]["target"], tick)
    sequence.append(sleep)
    tick += 1
    tick = _hold(sequence, sleep, tick, 7)

    wake = _retick(temporal["waking"]["target"], tick)
    sequence.append(wake)
    tick += 1
    tick = _hold(sequence, wake, tick, 6)

    wake_exit = _retick(temporal["wake_exit"]["target"], tick)
    sequence.append(wake_exit)
    tick += 1

    rain = _retick(godot["spring_rain_idle"]["target"], tick, activity="idle", pose="idle")
    rain["creature"]["carrying"] = None
    sequence.append(rain)
    tick += 1

    night = _retick(godot["winter_warm_night"]["target"], tick)
    night["creature"]["carrying"] = None
    sequence.append(night)

    return {
        "schema": SCHEMA,
        "frame_schema": "terrarium.frame.v1",
        "recommended_browser_query": "?terrarium_debug=1&terrarium_poll_ms=300",
        "purpose": "Exercise actual exported Godot Web timing, continuity, action lifetime, attachment, support choreography, environment mapping, duplicate ticks, and older ticks without touching the living world.",
        "sequences": {"composite": sequence},
        "required_semantic_motions": [
            "idle",
            "walk",
            "inspect",
            "nudge",
            "groom",
            "stretch",
            "loaf",
            "rest",
            "look",
            "window_watch",
            "carry",
            "place",
            "sleep",
            "wake",
        ],
        "expected_adapter_ignores": {"duplicate": 1, "older": 1},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/godot-art-gate/web-deep-debug/fixtures.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
