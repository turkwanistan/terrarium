#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrarium.engine import Simulation
from terrarium.models import initial_state
from terrarium.spatial import (
    BLOCKERS,
    SLEEP_SUPPORT_ANCHOR,
    SPATIAL_SCHEMA,
    point_is_walkable,
    route_blocker_hits,
    zone_anchor,
)

FIXED = "2026-01-01T00:00:00Z"


def _inside_strict(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
    x0, y0, x1, y1 = rect
    return x0 < x < x1 and y0 < y < y1


def _run(seed: int, steps: int) -> tuple[dict, list[dict]]:
    state = initial_state(seed, created_at=FIXED)
    sim = Simulation()
    records: list[dict] = []
    for tick in range(1, steps + 1):
        before = state
        _, _, details, state = sim.step(state)
        c = state["creature"]
        route = [(int(p["x"]), int(p["y"])) for p in details.get("route", [])]
        source = (int(details.get("source_x", before["creature"]["x"])), int(details.get("source_y", before["creature"]["y"])))
        allow_sleep = details.get("supported_action") == "sleep" or source == (
            SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"]
        )
        records.append({
            "tick": tick,
            "action": details.get("action"),
            "decision": bool(details.get("decision", True)),
            "from_zone": details.get("from_zone"),
            "to_zone": details.get("to_zone"),
            "source": source,
            "route": route,
            "route_hits": route_blocker_hits(source, route, allow_sleep_support=allow_sleep) if route else [],
            "endpoint": (int(c["x"]), int(c["y"])),
            "zone": c["zone"],
            "activity": c["activity"],
            "approach": None if details.get("approach_x") is None else (int(details["approach_x"]), int(details["approach_y"])),
            "semantic_target": None if details.get("target_x") is None else (int(details["target_x"]), int(details["target_y"])),
            "contact": None if details.get("contact_x") is None else (int(details["contact_x"]), int(details["contact_y"])),
            "spatial_schema": details.get("spatial_schema"),
            "carrying": c.get("carrying"),
        })
    return state, records


def evaluate(seed: int, steps: int) -> dict:
    final, records = _run(seed, steps)
    final2, records2 = _run(seed, steps)
    routed = [r for r in records if r["route"]]
    blocker_hits = [hit for r in routed for hit in r["route_hits"]]
    endpoint_mismatches = [r for r in routed if r["approach"] != r["endpoint"]]
    invalid_awake = [
        r for r in records
        if r["activity"] not in {"sleep", "wake"}
        and any(_inside_strict(r["endpoint"][0], r["endpoint"][1], rect) for rect in BLOCKERS.values())
    ]
    sleep_decisions = [r for r in records if r["decision"] and r["action"] == "sleep"]
    unsupported_sleep = [
        r for r in records if r["activity"] == "sleep"
        and (r["zone"] != "sleeping_nook" or r["endpoint"] != (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"]))
    ]
    window_actions = [r for r in records if r["decision"] and r["action"] == "look_outside"]
    bad_window = [r for r in window_actions if r["endpoint"] != zone_anchor("window")]
    movement = [r for r in records if r["decision"] and r["action"] in {"walk", "explore"}]
    bad_zone_arrivals = [r for r in movement if r["to_zone"] and r["endpoint"] != zone_anchor(r["to_zone"])]
    targeted = [r for r in records if r["decision"] and r["action"] in {"inspect", "carry", "place"} and r["semantic_target"]]
    separated = [r for r in targeted if r["approach"] and r["approach"] != r["semantic_target"]]
    contacted = [r for r in targeted if r["contact"] is not None]
    multi_segment = [r for r in routed if len(r["route"]) >= 2]
    carried_routes = [r for r in routed if r["carrying"] is not None or r["action"] == "place"]
    route_schema_mismatches = [r for r in routed if r["spatial_schema"] != SPATIAL_SCHEMA]
    checks = {
        "deterministic_execution": records == records2 and final == final2,
        "all_authored_zone_anchors_walkable": all(point_is_walkable(zone_anchor(zone)) for zone in ("sleeping_nook", "window", "open_space", "collection_shelf", "activity_corner")),
        "no_route_blocker_intersections": not blocker_hits,
        "route_endpoints_match_authoritative_approach": not endpoint_mismatches,
        "no_invalid_awake_furniture_occupancy": not invalid_awake,
        "sleep_always_supported": bool(sleep_decisions) and not unsupported_sleep,
        "window_watch_always_supported": bool(window_actions) and not bad_window,
        "zone_arrivals_use_authored_anchors": bool(movement) and not bad_zone_arrivals,
        "semantic_target_separated_from_physical_approach": bool(targeted) and len(separated) == len(targeted),
        "targeted_actions_have_reachable_contact": bool(targeted) and len(contacted) == len(targeted),
        "multi_segment_navigation_exercised": bool(multi_segment),
        "carried_multi_route_navigation_exercised": bool(carried_routes),
        "spatial_schema_recorded_on_routes": not route_schema_mismatches,
    }
    return {
        "schema": "terrarium.spatial-evaluation.v1",
        "seed": seed,
        "steps": steps,
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "routed_actions": len(routed),
            "multi_segment_routes": len(multi_segment),
            "max_route_points": max((len(r["route"]) for r in routed), default=0),
            "blocker_intersections": len(blocker_hits),
            "invalid_awake_endpoints": len(invalid_awake),
            "sleep_decisions": len(sleep_decisions),
            "window_watch_decisions": len(window_actions),
            "targeted_object_actions": len(targeted),
            "targeted_actions_with_distinct_approach": len(separated),
            "targeted_actions_with_contact": len(contacted),
            "carried_routes": len(carried_routes),
            "route_actions": dict(sorted(Counter(str(r["action"]) for r in routed).items())),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--steps", type=int, default=500)
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
