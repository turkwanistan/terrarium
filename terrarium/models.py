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
RULES_VERSION = "terrarium-rules-v7-object-identity"
BEHAVIOR_CONTEXT_SCHEMA = "terrarium.behavior-context.v1"
HABIT_PROFILE_SCHEMA = "terrarium.habits.v1"
AFFORDANCE_HISTORY_SCHEMA = "terrarium.affordances.v1"
OBJECT_AFFORDANCE_SCHEMA = "terrarium.object-affordances.v1"
SITUATIONAL_EVENTS_SCHEMA = "terrarium.situational-events.v1"
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

# Iteration 8D gives the six persistent objects explicit identities instead of
# routing every object through the same inspect -> nudge/carry graph. These
# archetypes are canonical world facts; the renderer only visualizes them.
OBJECT_IDENTITIES: dict[str, dict[str, str]] = {
    "blue_stone": {"archetype": "rolling", "default_state": "settled"},
    "acorn": {"archetype": "rolling", "default_state": "settled"},
    "red_thread": {"archetype": "soft_nesting", "default_state": "loose"},
    "amber_leaf": {"archetype": "delicate", "default_state": "fresh"},
    "shell": {"archetype": "keepsake", "default_state": "handled"},
    "glass_star": {"archetype": "keepsake", "default_state": "handled"},
}

OBJECT_ARCHETYPE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "rolling": ("inspect", "carry", "nudge"),
    "soft_nesting": ("inspect", "carry", "nudge"),
    "delicate": ("inspect", "carry"),
    "keepsake": ("inspect", "carry"),
}

def normalize_object_identity(obj: dict[str, Any]) -> dict[str, Any]:
    """Add/repair additive 8D identity fields without resetting legacy state."""
    identity = OBJECT_IDENTITIES.get(str(obj.get("id")))
    if identity is None:
        identity = {"archetype": "keepsake", "default_state": "handled"}
    obj["affordance_schema"] = OBJECT_AFFORDANCE_SCHEMA
    obj["archetype"] = str(identity["archetype"])
    valid_states = {
        "rolling": {"settled", "rolled"},
        "soft_nesting": {"loose", "rumpled", "nested"},
        "delicate": {"fresh", "handled"},
        "keepsake": {"handled", "displayed"},
    }[obj["archetype"]]
    current = str(obj.get("interaction_state") or identity["default_state"])
    obj["interaction_state"] = current if current in valid_states else str(identity["default_state"])
    obj["state_transitions"] = max(0, int(obj.get("state_transitions", 0)))
    return obj


def object_affordances(obj: dict[str, Any]) -> tuple[str, ...]:
    """Return the currently available object-specific affordances."""
    normalize_object_identity(obj)
    archetype = str(obj["archetype"])
    state = str(obj["interaction_state"])
    available = list(OBJECT_ARCHETYPE_AFFORDANCES[archetype])
    if archetype == "rolling" and state == "rolled":
        available = [name for name in available if name != "nudge"]
    elif archetype == "soft_nesting":
        nestable_zone = str(obj.get("zone")) in {"open_space", "sleeping_nook"}
        if state == "loose" and not nestable_zone:
            available = [name for name in available if name != "nudge"]
        elif state == "rumpled":
            available = [name for name in available if name != "nudge"]
            if nestable_zone:
                available.append("nest")
        elif state == "nested":
            available = [name for name in available if name != "nudge"]
    return tuple(available)


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
        obj = {
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
        objects.append(normalize_object_identity(obj))
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
            "situational_events": {
                "schema": SITUATIONAL_EVENTS_SCHEMA,
                "migration_origin": "native",
                "active": None,
                "recent": [],
                "started_counts": {name: 0 for name in ("sunlight", "bird", "rain_intensify", "thunder", "moth", "leaf_tap")},
                "outcome_counts": {"ignored": 0, "oriented": 0, "deferred": 0, "interrupted": 0, "engaged": 0},
            },
        },
        "objects": objects,
    }


def clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(state)
