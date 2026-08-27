from __future__ import annotations

from typing import Any

from .models import FRAME_HEIGHT, FRAME_WIDTH

FRAME_SCHEMA = "terrarium.frame.v1"


def make_frame(state: dict[str, Any], *, last_event: dict[str, Any] | None = None) -> dict[str, Any]:
    creature = state["creature"]
    commitment = creature.get("behavior_commitment") or {}
    aftermath = state["habitat"].get("activity_aftermath") or {}
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
            "intent_action": commitment.get("action"),
            "intent_ticks_remaining": int(commitment.get("ticks_remaining", 0)),
            "target_object_id": creature.get("focus_object_id"),
        },
        "objects": [
            {k: obj[k] for k in ("id", "name", "kind", "x", "y", "zone", "state", "carried_by", "times_moved", "times_inspected")}
            for obj in state["objects"]
        ],
        "habitat": {
            "shelf_count": state["habitat"]["shelf_count"],
            "path_wear": state["habitat"]["path_wear"],
            "marks": list(state["habitat"]["marks"]),
            "activity_aftermath": {
                key: int(aftermath.get(key, 0))
                for key in ("sleep_nook_ticks", "sleep_nook_bouts", "window_watches", "wet_window_watches", "activity_corner_uses")
            },
        },
        "last_event": None
        if not last_event
        else {
            "event_id": last_event["event_id"],
            "type": last_event["type"],
            "summary": last_event["summary"],
            "action": (last_event.get("details") or {}).get("action"),
            "object_id": (last_event.get("details") or {}).get("object_id"),
            "from_zone": (last_event.get("details") or {}).get("from_zone"),
            "to_zone": (last_event.get("details") or {}).get("to_zone"),
            "decision": bool((last_event.get("details") or {}).get("decision", True)),
            "intent_action": (last_event.get("details") or {}).get("intent_action", (last_event.get("details") or {}).get("action")),
            "target_x": (last_event.get("details") or {}).get("target_x"),
            "target_y": (last_event.get("details") or {}).get("target_y"),
        },
    }
