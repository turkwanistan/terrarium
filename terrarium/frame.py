from __future__ import annotations

from typing import Any

from .models import FRAME_HEIGHT, FRAME_WIDTH

FRAME_SCHEMA = "terrarium.frame.v1"


def make_frame(state: dict[str, Any], *, last_event: dict[str, Any] | None = None) -> dict[str, Any]:
    creature = state["creature"]
    return {
        "schema": FRAME_SCHEMA,
        "frame_version": 1,
        "logical_width": FRAME_WIDTH,
        "logical_height": FRAME_HEIGHT,
        "tick": state["tick"],
        "world_minutes": state["world_minutes"],
        "lighting": state["habitat"]["lighting"],
        "weather": state["habitat"]["weather"],
        "creature": {
            "id": creature["id"],
            "name": creature["name"],
            "x": creature["x"],
            "y": creature["y"],
            "zone": creature["zone"],
            "facing": creature["facing"],
            "pose": creature["activity"],
            "activity": creature["activity"],
            "expression": creature["expression"],
            "carrying": creature["carrying"],
        },
        "objects": [
            {k: obj[k] for k in ("id", "name", "kind", "x", "y", "zone", "state", "carried_by", "times_moved")}
            for obj in state["objects"]
        ],
        "habitat": {
            "shelf_count": state["habitat"]["shelf_count"],
            "path_wear": state["habitat"]["path_wear"],
            "marks": list(state["habitat"]["marks"]),
        },
        "last_event": None
        if not last_event
        else {
            "event_id": last_event["event_id"],
            "type": last_event["type"],
            "summary": last_event["summary"],
        },
    }
