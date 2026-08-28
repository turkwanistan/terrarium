from __future__ import annotations

from typing import Any

from .models import OBJECT_AFFORDANCE_SCHEMA, object_affordances

from .models import FRAME_HEIGHT, FRAME_WIDTH
from .spatial import SPATIAL_SCHEMA
from .situations import event_frame

FRAME_SCHEMA = "terrarium.frame.v1"


def make_frame(state: dict[str, Any], *, last_event: dict[str, Any] | None = None) -> dict[str, Any]:
    creature = state["creature"]
    commitment = creature.get("behavior_commitment") or {}
    aftermath = state["habitat"].get("activity_aftermath") or {}
    seasonal = state["habitat"].get("seasonal_clock") or {}
    return {
        "schema": FRAME_SCHEMA,
        "frame_version": 1,
        "logical_width": FRAME_WIDTH,
        "logical_height": FRAME_HEIGHT,
        "tick": state["tick"],
        "world_minutes": state["world_minutes"],
        "lighting": state["habitat"]["lighting"],
        "weather": state["habitat"]["weather"],
        "season": {
            "schema": seasonal.get("schema"),
            "name": seasonal.get("season", "spring"),
            "index": int(seasonal.get("season_index", 0)),
            "stage": seasonal.get("stage", "early"),
            "stage_index": int(seasonal.get("stage_index", 0)),
            "progress": float(seasonal.get("progress", 0.0)),
            "cycle_index": int(seasonal.get("cycle_index", 0)),
            "cadence_days_per_season": int(seasonal.get("cadence_days_per_season", 21)),
            "stage_days": int(seasonal.get("stage_days", 7)),
        },
        "world_event": event_frame(state),
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
            {
                **{k: obj[k] for k in ("id", "name", "kind", "x", "y", "zone", "state", "carried_by", "times_moved", "times_inspected", "times_nudged")},
                "affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                "archetype": obj["archetype"],
                "interaction_state": obj["interaction_state"],
                "state_transitions": int(obj.get("state_transitions", 0)),
                "available_affordances": list(object_affordances(obj)),
            }
            for obj in state["objects"]
        ],
        "habitat": {
            "shelf_count": state["habitat"]["shelf_count"],
            "path_wear": state["habitat"]["path_wear"],
            "marks": list(state["habitat"]["marks"]),
            "activity_aftermath": {
                key: int(aftermath.get(key, 0))
                for key in ("sleep_nook_ticks", "sleep_nook_bouts", "window_watches", "wet_window_watches", "activity_corner_uses", "loaf_sessions", "groom_sessions", "stretch_sessions", "object_nudges", "arrangement_places", "weather_reactions")
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
            "contact_x": (last_event.get("details") or {}).get("contact_x"),
            "contact_y": (last_event.get("details") or {}).get("contact_y"),
            "spatial_schema": (last_event.get("details") or {}).get("spatial_schema"),
            "source_x": (last_event.get("details") or {}).get("source_x"),
            "source_y": (last_event.get("details") or {}).get("source_y"),
            "approach_x": (last_event.get("details") or {}).get("approach_x"),
            "approach_y": (last_event.get("details") or {}).get("approach_y"),
            "route_length": (last_event.get("details") or {}).get("route_length"),
            "route": [dict(point) for point in ((last_event.get("details") or {}).get("route") or [])],
            "supported_action": (last_event.get("details") or {}).get("supported_action"),
            "activity_family": (last_event.get("details") or {}).get("activity_family"),
            "result_x": (last_event.get("details") or {}).get("result_x"),
            "result_y": (last_event.get("details") or {}).get("result_y"),
            "object_affordance_schema": (last_event.get("details") or {}).get("object_affordance_schema"),
            "object_archetype": (last_event.get("details") or {}).get("object_archetype"),
            "object_affordance": (last_event.get("details") or {}).get("object_affordance"),
            "object_state_before": (last_event.get("details") or {}).get("object_state_before"),
            "object_state_after": (last_event.get("details") or {}).get("object_state_after"),
            "world_event_id": (last_event.get("details") or {}).get("world_event_id"),
            "world_event_type": (last_event.get("details") or {}).get("world_event_type"),
            "world_event_role": (last_event.get("details") or {}).get("world_event_role"),
            "world_event_attention_status": (last_event.get("details") or {}).get("world_event_attention_status"),
            "world_event_started": (last_event.get("details") or {}).get("world_event_started"),
            "world_event_ended": (last_event.get("details") or {}).get("world_event_ended"),
        },
        "spatial": {"schema": SPATIAL_SCHEMA},
    }
