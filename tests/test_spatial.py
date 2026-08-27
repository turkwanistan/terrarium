from __future__ import annotations

from terrarium.engine import Simulation
from terrarium.models import ZONES, initial_state
from terrarium.spatial import (
    BLOCKERS,
    SLEEP_SUPPORT_ANCHOR,
    SPATIAL_SCHEMA,
    interaction_approach,
    point_is_walkable,
    route_between,
    route_blocker_hits,
    zone_anchor,
)

FIXED = "2026-01-01T00:00:00Z"


def _inside_strict(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
    x0, y0, x1, y1 = rect
    return x0 < x < x1 and y0 < y < y1


def test_authored_zone_anchors_are_walkable_and_route_graph_avoids_blockers():
    for zone in ZONES:
        assert point_is_walkable(zone_anchor(zone)), zone
    for source_zone in ZONES:
        for destination_zone in ZONES:
            if source_zone == destination_zone:
                continue
            source = zone_anchor(source_zone)
            destination = zone_anchor(destination_zone)
            first = route_between(source, source_zone, destination, destination_zone)
            second = route_between(source, source_zone, destination, destination_zone)
            assert first == second
            assert first[-1] == destination
            assert route_blocker_hits(source, first) == []


def test_surface_interactions_use_physical_approach_not_semantic_target_center():
    state = initial_state(1701, created_at=FIXED)
    current = state["creature"]
    for obj in state["objects"]:
        approach = interaction_approach(
            zone=obj["zone"], target_x=obj["x"], target_y=obj["y"],
            current_x=current["x"], current_y=current["y"],
        )
        assert approach != (obj["x"], obj["y"])
        assert point_is_walkable(approach)


def test_500_tick_spatial_execution_is_deterministic_blocker_free_and_supported():
    def run():
        state = initial_state(1701, created_at=FIXED)
        sim = Simulation()
        evidence = []
        non_nook_sleep = None
        sleep_exit = None
        for tick in range(1, 501):
            before = state
            _, _, details, state = sim.step(state)
            route = [(p["x"], p["y"]) for p in details.get("route", [])]
            if route:
                source = (details["source_x"], details["source_y"])
                allow_sleep = details.get("supported_action") == "sleep" or source == (
                    SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"]
                )
                assert route_blocker_hits(source, route, allow_sleep_support=allow_sleep) == []
                assert route[-1] == (details["approach_x"], details["approach_y"])
                assert route[-1] == (state["creature"]["x"], state["creature"]["y"])
                assert details["spatial_schema"] == SPATIAL_SCHEMA
            c = state["creature"]
            if c["activity"] in {"sleep", "wake"}:
                assert c["zone"] == "sleeping_nook"
                assert (c["x"], c["y"]) == (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"])
            else:
                assert not any(_inside_strict(c["x"], c["y"], rect) for rect in BLOCKERS.values())
            if details.get("decision") and details.get("action") == "sleep" and before["creature"]["zone"] != "sleeping_nook":
                non_nook_sleep = (tick, details.get("route"))
            if route and (details["source_x"], details["source_y"]) == (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"]):
                sleep_exit = (tick, details.get("route"))
            evidence.append((details.get("action"), details.get("from_zone"), details.get("to_zone"), details.get("route"), c["x"], c["y"]))
        assert non_nook_sleep is not None
        assert sleep_exit is not None
        return evidence

    assert run() == run()
