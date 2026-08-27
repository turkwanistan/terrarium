from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from .spatial import ZONE_ANCHORS

FRAME_WIDTH = 800
FRAME_HEIGHT = 480
STATE_SCHEMA_VERSION = 1
RULES_VERSION = "terrarium-rules-v5-behavioral-repertoire"
BEHAVIOR_CONTEXT_SCHEMA = "terrarium.behavior-context.v1"
HABIT_PROFILE_SCHEMA = "terrarium.habits.v1"
AFFORDANCE_HISTORY_SCHEMA = "terrarium.affordances.v1"
HABIT_CONTEXTS = ("dawn", "day", "dusk", "night")
RNG_STREAM_VERSION = "terrarium-rules-v3-routine-coherence"
EVENT_VERSION = 1
WEATHER_STREAM_VERSION = "terrarium.weather.v2"

ZONES: dict[str, dict[str, int]] = {name: dict(anchor) for name, anchor in ZONE_ANCHORS.items()}


# Authored object staging points make autonomous arrangements read as part of
# the habitat instead of as random coordinate scatter. These are presentation-
# meaningful world coordinates, not renderer-owned state.
PLACEMENT_SLOTS: dict[str, list[tuple[int, int]]] = {
    "sleeping_nook": [(238, 390), (248, 400), (258, 388), (266, 402), (242, 410), (270, 412)],
    "window": [(86, 268), (118, 279), (155, 266), (190, 278), (225, 267), (252, 281)],
    "open_space": [(326, 365), (365, 392), (404, 369), (443, 395), (482, 367), (505, 402)],
    "collection_shelf": [(620, 292), (640, 294), (660, 292), (680, 294), (700, 292), (720, 294)],
    "activity_corner": [(606, 340), (620, 338), (634, 342), (648, 338), (612, 354), (638, 354)],
}

OBJECT_BLUEPRINTS = [
    ("blue_stone", "Blue stone", "stone", "open_space", 372, 333),
    ("amber_leaf", "Amber leaf", "leaf", "window", 212, 263),
    ("acorn", "Acorn", "seed", "activity_corner", 612, 360),
    ("shell", "Tiny shell", "shell", "open_space", 460, 352),
    ("red_thread", "Red thread", "thread", "sleeping_nook", 150, 392),
    ("glass_star", "Glass star", "trinket", "activity_corner", 704, 338),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def lighting_for(world_minutes: int) -> str:
    minute = world_minutes % 1440
    if 360 <= minute < 480:
        return "dawn"
    if 480 <= minute < 1050:
        return "day"
    if 1050 <= minute < 1170:
        return "dusk"
    return "night"


def weather_for(world_minutes: int, seed: int) -> str:
    # Pure deterministic ambient cycle independent from action RNG. Hashing the
    # three-hour block avoids low-bit LCG aliasing (canonical seed 1701 used to
    # remain clear indefinitely) while keeping weather calm and replay-exact.
    block = int(world_minutes) // 180
    material = f"{int(seed)}:{WEATHER_STREAM_VERSION}:{block}".encode("utf-8")
    bucket = int.from_bytes(hashlib.sha256(material).digest()[:2], "big") % 10
    if bucket <= 1:
        return "rain"
    if bucket == 2:
        return "mist"
    return "clear"


def initial_state(seed: int, *, created_at: str | None = None) -> dict[str, Any]:
    created = created_at or utc_now()
    objects = []
    for oid, name, kind, zone, x, y in OBJECT_BLUEPRINTS:
        objects.append(
            {
                "id": oid,
                "name": name,
                "kind": kind,
                "zone": zone,
                "x": x,
                "y": y,
                "state": "placed",
                "carried_by": None,
                "times_inspected": 0,
                "times_moved": 0,
                "times_nudged": 0,
            }
        )
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "rules_version": RULES_VERSION,
        "event_version": EVENT_VERSION,
        "seed": int(seed),
        "tick": 0,
        "world_minutes": 420,
        "created_at": created,
        "creature": {
            "id": "creature-1",
            "name": "Moss",
            "zone": "sleeping_nook",
            "x": ZONES["sleeping_nook"]["x"],
            "y": ZONES["sleeping_nook"]["y"],
            "facing": "right",
            "activity": "idle",
            "expression": "content",
            "energy": 0.76,
            "comfort": 0.72,
            "curiosity": 0.58,
            "carrying": None,
            "recent_actions": [],
            "focus_object_id": None,
            "behavior_commitment": {"action": None, "ticks_remaining": 0, "object_id": None},
            "behavior_context": {
                "schema": BEHAVIOR_CONTEXT_SCHEMA,
                "recent_zones": ["sleeping_nook"],
                "recent_objects": [],
                "intent": None,
            },
            "habit_profile": {
                "schema": HABIT_PROFILE_SCHEMA,
                "migration_origin": "native",
                "experience_count": 0,
                "zone_affinity": {name: 0.0 for name in ZONES},
                "object_affinity": {obj["id"]: 0.0 for obj in objects},
                "context_zone_affinity": {
                    context: {name: 0.0 for name in ZONES} for context in HABIT_CONTEXTS
                },
            },
        },
        "habitat": {
            "lighting": lighting_for(420),
            "weather": weather_for(420, int(seed)),
            "shelf_count": 0,
            "path_wear": {name: 0 for name in ZONES},
            "marks": [],
            "activity_aftermath": {
                "sleep_nook_ticks": 0,
                "sleep_nook_bouts": 0,
                "window_watches": 0,
                "wet_window_watches": 0,
                "activity_corner_uses": 0,
                "loaf_sessions": 0,
                "groom_sessions": 0,
                "stretch_sessions": 0,
                "object_nudges": 0,
                "arrangement_places": 0,
                "weather_reactions": 0,
            },
            "affordance_history": {
                "schema": AFFORDANCE_HISTORY_SCHEMA,
                "completed_families": {},
                "object_nudges": {},
                "zone_comfort": {name: 0 for name in ZONES},
                "zone_arrangements": {name: 0 for name in ZONES},
                "last_weather_reaction_block": -1,
            },
        },
        "objects": objects,
    }


def clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(state)
