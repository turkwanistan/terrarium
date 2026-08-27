from __future__ import annotations

from math import hypot
from typing import Any, Iterable

# Authoritative room-space model in the canonical 800x480 semantic coordinate
# system.  The renderer consumes routes/anchors but does not decide where Moss
# may stand.
SPATIAL_SCHEMA = "terrarium.spatial.v1"

ZONE_ANCHORS: dict[str, dict[str, int]] = {
    "sleeping_nook": {"x": 296, "y": 392},       # open floor at the bed's right side
    "window": {"x": 168, "y": 316},             # floor-side viewing stance
    "open_space": {"x": 405, "y": 378},         # rug / central circulation
    "collection_shelf": {"x": 554, "y": 312},   # left/front access to shelf
    "activity_corner": {"x": 554, "y": 372},    # open side of desk
}

# A deliberately small set of authored places Moss can treat as familiar
# destinations.  They reuse the compact navigation graph rather than creating
# a grid of arbitrary nodes.  Behavior may prefer these zones for the named
# purpose; physical authority remains the ordinary zone anchor.
FAVORITE_SPOTS: dict[str, dict[str, int | str]] = {
    "bedside_rest": {"zone": "sleeping_nook", "x": 296, "y": 392, "purpose": "rest"},
    "window_watch": {"zone": "window", "x": 168, "y": 316, "purpose": "observe"},
    "rug_rest": {"zone": "open_space", "x": 405, "y": 378, "purpose": "idle"},
    "activity_settle": {"zone": "activity_corner", "x": 554, "y": 372, "purpose": "settle"},
}

SLEEP_SUPPORT_ANCHOR = {"x": 222, "y": 394}

# Visual furniture footprints expanded by a small anchor-clearance margin.  The
# bed is special: ordinary navigation may not enter it, while the explicit
# sleep-support ingress/egress is allowed.
BLOCKERS: dict[str, tuple[int, int, int, int]] = {
    "bed": (34, 328, 278, 454),
    "window_perch": (80, 288, 256, 310),
    "collection_tray": (596, 282, 748, 308),
    "desk": (568, 290, 790, 434),
    "bowls": (496, 398, 628, 450),
}

WALKABLE_BOUNDS = (28, 306, 772, 456)

# Small authored circulation graph.  These are execution waypoints for a
# semantic decision, never additional behavior decisions.
NAV_NODES: dict[str, tuple[int, int]] = {
    "center": (405, 378),
    "left_turn": (300, 324),
    "bed_gate": (296, 392),
    "right_turn": (554, 326),
    "window": (168, 316),
    "shelf": (554, 312),
    "desk": (554, 372),
}

ZONE_TO_CENTER: dict[str, tuple[str, ...]] = {
    "open_space": ("center",),
    "window": ("window", "left_turn", "center"),
    "sleeping_nook": ("bed_gate", "center"),
    "collection_shelf": ("shelf", "right_turn", "center"),
    "activity_corner": ("desk", "center"),
}

SURFACE_ZONES = {"window", "collection_shelf", "activity_corner", "sleeping_nook"}


def point(x: int | float, y: int | float) -> dict[str, int]:
    return {"x": int(round(x)), "y": int(round(y))}


def _same(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] == b[0] and a[1] == b[1]


def _dedupe(points: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for item in points:
        if not result or not _same(result[-1], item):
            result.append(item)
    return result


def zone_anchor(zone: str) -> tuple[int, int]:
    anchor = ZONE_ANCHORS[zone]
    return int(anchor["x"]), int(anchor["y"])


def route_between(
    source: tuple[int, int],
    source_zone: str,
    destination: tuple[int, int],
    destination_zone: str,
) -> list[tuple[int, int]]:
    """Return deterministic authored route points excluding ``source``.

    Ordinary zone travel goes through the central circulation graph.  If the
    source is the supported sleep anchor, the first point is the bed's open-side
    gate.  Dynamic open-space destinations are appended after the central node.
    """
    if source_zone not in ZONE_TO_CENTER or destination_zone not in ZONE_TO_CENTER:
        raise KeyError(f"unknown navigation zone: {source_zone!r} -> {destination_zone!r}")

    if source_zone == destination_zone:
        if _same(source, destination):
            return []
        if source_zone == "sleeping_nook" and _same(source, (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"])):
            points = [source, NAV_NODES["bed_gate"]]
            if not _same(points[-1], destination):
                points.append(destination)
            return _dedupe(points)[1:]
        anchor = zone_anchor(source_zone)
        points = [source]
        if source_zone != "open_space" and not _same(source, anchor):
            points.append(anchor)
        if not _same(points[-1], destination):
            points.append(destination)
        return _dedupe(points)[1:]

    source_path = [NAV_NODES[name] for name in ZONE_TO_CENTER[source_zone]]
    destination_path = [NAV_NODES[name] for name in reversed(ZONE_TO_CENTER[destination_zone])]
    points: list[tuple[int, int]] = [source]

    if source_zone == "sleeping_nook" and _same(source, (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"])):
        points.append(NAV_NODES["bed_gate"])

    # Skip the first authored point when it is already the source endpoint.
    for candidate in source_path:
        if not _same(points[-1], candidate):
            points.append(candidate)
    for candidate in destination_path:
        if not _same(points[-1], candidate):
            points.append(candidate)
    if not _same(points[-1], destination):
        points.append(destination)

    return _dedupe(points)[1:]


def route_length(source: tuple[int, int], route: Iterable[tuple[int, int]]) -> float:
    total = 0.0
    prior = source
    for current in route:
        total += hypot(current[0] - prior[0], current[1] - prior[1])
        prior = current
    return total


def _point_in_rect_strict(p: tuple[float, float], rect: tuple[int, int, int, int]) -> bool:
    x0, y0, x1, y1 = rect
    return x0 < p[0] < x1 and y0 < p[1] < y1


def point_is_walkable(p: tuple[int, int]) -> bool:
    x0, y0, x1, y1 = WALKABLE_BOUNDS
    if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
        return False
    return not any(_point_in_rect_strict(p, rect) for rect in BLOCKERS.values())


def _segment_hits_rect(a: tuple[int, int], b: tuple[int, int], rect: tuple[int, int, int, int]) -> bool:
    """Liang-Barsky intersection against a slightly shrunken blocker interior."""
    x0, y0, x1, y1 = rect
    eps = 0.01
    x0 += eps; y0 += eps; x1 -= eps; y1 -= eps
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    p = (-dx, dx, -dy, dy)
    q = (a[0] - x0, x1 - a[0], a[1] - y0, y1 - a[1])
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            if t > u2:
                return False
            u1 = max(u1, t)
        else:
            if t < u1:
                return False
            u2 = min(u2, t)
    return u1 <= u2


def route_blocker_hits(
    source: tuple[int, int],
    route: Iterable[tuple[int, int]],
    *,
    allow_sleep_support: bool = False,
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    prior = source
    route_list = list(route)
    for index, current in enumerate(route_list):
        for name, rect in BLOCKERS.items():
            if allow_sleep_support and name == "bed" and index == len(route_list) - 1 and _same(current, (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"])):
                continue
            if allow_sleep_support and name == "bed" and index == 0 and _same(prior, (SLEEP_SUPPORT_ANCHOR["x"], SLEEP_SUPPORT_ANCHOR["y"])):
                continue
            if _segment_hits_rect(prior, current, rect):
                hits.append({"segment": index, "blocker": name, "from": point(*prior), "to": point(*current)})
        prior = current
    return hits


def interaction_approach(
    *,
    zone: str,
    target_x: int,
    target_y: int,
    current_x: int,
    current_y: int,
) -> tuple[int, int]:
    """Choose an authoritative physical stance distinct from semantic target."""
    if zone in SURFACE_ZONES:
        return zone_anchor(zone)

    # Open-space objects get a nearby floor stance.  Candidate ordering is
    # deterministic and biased to the current side to avoid needless crossing.
    side = -1 if current_x <= target_x else 1
    candidates = [
        (target_x + side * 46, target_y),
        (target_x - side * 46, target_y),
        (target_x, target_y - 42),
        (target_x, target_y + 42),
    ]
    valid = [candidate for candidate in candidates if point_is_walkable(candidate)]
    if not valid:
        return zone_anchor("open_space")
    valid.sort(key=lambda candidate: ((candidate[0] - current_x) ** 2 + (candidate[1] - current_y) ** 2, candidate[1], candidate[0]))
    return valid[0]




def interaction_contact(*, zone: str, target_x: int, target_y: int, approach: tuple[int, int]) -> tuple[int, int]:
    """Return the reachable action-contact point for a semantic target.

    Persisted objects may live on elevated/deep authored surfaces from earlier
    checkpoints.  Moss keeps targeting that exact object, but acts against the
    reachable front edge instead of stretching through furniture.
    """
    if zone == "collection_shelf":
        return (592, 300)
    if zone == "activity_corner":
        return (584, 344)
    if zone == "sleeping_nook":
        return (276, 392)
    if zone == "window":
        return (max(118, min(218, int(target_x))), 300)
    return (int(target_x), int(target_y))


def route_payload(source: tuple[int, int], route: Iterable[tuple[int, int]]) -> list[dict[str, int]]:
    del source
    return [point(x, y) for x, y in route]
