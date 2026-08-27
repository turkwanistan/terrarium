from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

FRAME_WIDTH = 800
FRAME_HEIGHT = 480
STATE_SCHEMA_VERSION = 1
RULES_VERSION = "gen17-rules-v1"
EVENT_VERSION = 1

ZONES: dict[str, dict[str, int]] = {
    "sleeping_nook": {"x": 118, "y": 372},
    "window": {"x": 168, "y": 132},
    "open_space": {"x": 405, "y": 294},
    "collection_shelf": {"x": 682, "y": 150},
    "activity_corner": {"x": 655, "y": 372},
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
    # Pure, deterministic ambient cycle; action RNG never affects weather.
    block = world_minutes // 180
    v = (seed * 1103515245 + block * 12345) & 0x7FFFFFFF
    bucket = v % 10
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
        },
        "habitat": {
            "lighting": lighting_for(420),
            "weather": weather_for(420, int(seed)),
            "shelf_count": 0,
            "path_wear": {name: 0 for name in ZONES},
            "marks": [],
        },
        "objects": objects,
    }


def clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(state)
