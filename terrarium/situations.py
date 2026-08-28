from __future__ import annotations

import hashlib
from typing import Any

from .models import ZONES
from .spatial import point_is_walkable, zone_anchor

SITUATIONAL_EVENTS_SCHEMA = "terrarium.situational-events.v1"
EVENT_CATALOG = ("sunlight", "bird", "rain_intensify", "thunder", "moth", "leaf_tap")
EVENT_SLOT_MINUTES = 40
RECENT_EVENT_LIMIT = 16
SAME_TYPE_COOLDOWN_MINUTES = 100

_EVENT_CONFIG: dict[str, dict[str, Any]] = {
    "sunlight": {"duration": 18, "salience": 0.58, "source_zone": "open_space", "engage_action": "loaf"},
    "bird": {"duration": 11, "salience": 0.72, "source_zone": "window", "source_x": 206, "source_y": 126, "engage_action": "look_outside"},
    "rain_intensify": {"duration": 13, "salience": 0.64, "source_zone": "window", "source_x": 174, "source_y": 148, "engage_action": "look_outside"},
    "thunder": {"duration": 8, "salience": 0.96, "source_zone": "window", "source_x": 184, "source_y": 112, "engage_action": "look_outside"},
    "moth": {"duration": 15, "salience": 0.68, "source_zone": "activity_corner", "source_x": 744, "source_y": 310, "engage_action": "react"},
    "leaf_tap": {"duration": 7, "salience": 0.52, "source_zone": "window", "source_x": 226, "source_y": 176, "engage_action": "look_outside"},
}


def _hash_bytes(*parts: object) -> bytes:
    return hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).digest()


def ensure_situational_events(state: dict[str, Any]) -> dict[str, Any]:
    habitat = state["habitat"]
    current = habitat.get("situational_events")
    if not isinstance(current, dict) or current.get("schema") != SITUATIONAL_EVENTS_SCHEMA:
        current = {
            "schema": SITUATIONAL_EVENTS_SCHEMA,
            "migration_origin": "neutral-existing-world",
            "active": None,
            "recent": [],
            "started_counts": {name: 0 for name in EVENT_CATALOG},
            "outcome_counts": {"ignored": 0, "oriented": 0, "deferred": 0, "interrupted": 0, "engaged": 0},
        }
        habitat["situational_events"] = current
    current["schema"] = SITUATIONAL_EVENTS_SCHEMA
    current.setdefault("migration_origin", "native")
    current["recent"] = [dict(item) for item in list(current.get("recent") or [])[-RECENT_EVENT_LIMIT:]]
    started = dict(current.get("started_counts") or {})
    current["started_counts"] = {name: max(0, int(started.get(name, 0))) for name in EVENT_CATALOG}
    outcomes = dict(current.get("outcome_counts") or {})
    current["outcome_counts"] = {
        name: max(0, int(outcomes.get(name, 0)))
        for name in ("ignored", "oriented", "deferred", "interrupted", "engaged")
    }
    active = current.get("active")
    if active is not None and not isinstance(active, dict):
        current["active"] = None
    return current


def _allowed_events(state: dict[str, Any]) -> list[str]:
    lighting = str(state["habitat"]["lighting"])
    weather = str(state["habitat"]["weather"])
    allowed: list[str] = []
    if lighting == "night":
        allowed += ["moth", "moth"]
    elif lighting in {"dawn", "day", "dusk"}:
        if weather == "clear":
            allowed += ["bird", "bird", "leaf_tap"]
            if lighting == "day":
                allowed += ["sunlight", "sunlight", "sunlight"]
        elif weather == "mist":
            allowed += ["bird", "leaf_tap"]
        if weather == "rain":
            allowed += ["rain_intensify", "rain_intensify", "thunder", "thunder", "leaf_tap"]
    if weather == "rain" and lighting == "night":
        allowed += ["rain_intensify", "thunder", "thunder"]
    return allowed


def _sunlight_position(event: dict[str, Any], now: int) -> tuple[int, int]:
    start = int(event["start_world_minute"])
    end = max(start + 1, int(event["end_world_minute"]))
    span = max(1, end - start)
    progress = max(0.0, min(1.0, (int(now) - start) / span))
    x = int(round(350 + 112 * progress))
    y = 380 + (4 if int(progress * 4) % 2 else 0)
    return x, y


def _event_source(event: dict[str, Any], now: int) -> tuple[str, int, int]:
    event_type = str(event["type"])
    if event_type == "sunlight":
        x, y = _sunlight_position(event, now)
        return "open_space", x, y
    config = _EVENT_CONFIG[event_type]
    zone = str(event.get("source_zone") or config["source_zone"])
    x = int(config.get("source_x", zone_anchor(zone)[0]))
    y = int(config.get("source_y", zone_anchor(zone)[1]))
    return zone, x, y


def event_target(event: dict[str, Any], now: int) -> dict[str, Any]:
    zone, source_x, source_y = _event_source(event, now)
    if str(event["type"]) == "sunlight":
        x, y = source_x, source_y
    else:
        x, y = zone_anchor(zone)
    if not point_is_walkable((x, y)):
        x, y = zone_anchor(zone)
    return {
        "zone": zone,
        "x": int(x),
        "y": int(y),
        "engage_action": str(_EVENT_CONFIG[str(event["type"])]["engage_action"]),
    }


def _start_event(state: dict[str, Any], event_type: str, slot: int, digest: bytes) -> dict[str, Any]:
    now = int(state["world_minutes"])
    config = _EVENT_CONFIG[event_type]
    duration = int(config["duration"]) + int(digest[3] % 4)
    event = {
        "id": f"evt-{int(state['seed'])}-{slot}-{event_type}",
        "type": event_type,
        "start_world_minute": now,
        "end_world_minute": now + duration,
        "salience": float(config["salience"]),
        "source_zone": str(config["source_zone"]),
        "attention_status": "pending",
        "outcome": None,
        "response_path": [],
        "noticed_at": None,
        "engaged_at": None,
        "interrupted_action": None,
        "follow_moves": 0,
    }
    zone, x, y = _event_source(event, now)
    event["source_zone"] = zone
    event["x"] = x
    event["y"] = y
    if event_type == "sunlight":
        event["temporary_affordance"] = {"kind": "sunlight_rest", "x": x, "y": y, "radius": 52}
    return event


def _finish_active(current: dict[str, Any], active: dict[str, Any], now: int) -> dict[str, Any]:
    raw_outcome = str(active.get("outcome") or "")
    response_path = list(active.get("response_path") or [])
    if raw_outcome == "engaged":
        outcome = "engaged"
    elif raw_outcome == "oriented" or any(step in {"noticed", "deferred", "interrupted"} for step in response_path):
        outcome = "oriented"
    else:
        outcome = "ignored"
    record = {
        "id": str(active["id"]),
        "type": str(active["type"]),
        "start_world_minute": int(active["start_world_minute"]),
        "end_world_minute": int(now),
        "outcome": outcome,
        "response_path": response_path,
    }
    current["recent"] = (list(current.get("recent") or []) + [record])[-RECENT_EVENT_LIMIT:]
    current["outcome_counts"][outcome] = int(current["outcome_counts"].get(outcome, 0)) + 1
    current["active"] = None
    return record


def update_situational_events(state: dict[str, Any]) -> dict[str, Any]:
    current = ensure_situational_events(state)
    now = int(state["world_minutes"])
    transition: dict[str, Any] = {"started": None, "ended": None}
    active = current.get("active")
    if isinstance(active, dict):
        if now >= int(active["end_world_minute"]):
            transition["ended"] = _finish_active(current, active, now)
            active = None
        else:
            zone, x, y = _event_source(active, now)
            active["source_zone"] = zone
            active["x"], active["y"] = x, y
            if active.get("type") == "sunlight":
                active["temporary_affordance"] = {"kind": "sunlight_rest", "x": x, "y": y, "radius": 52}

    if current.get("active") is None:
        slot = now // EVENT_SLOT_MINUTES
        digest = _hash_bytes(int(state["seed"]), SITUATIONAL_EVENTS_SCHEMA, slot)
        offset = 6 + int(digest[0] % 25)
        scheduled = now % EVENT_SLOT_MINUTES == offset
        if scheduled and int(digest[1] % 100) < 22:
            allowed = _allowed_events(state)
            if allowed:
                recent = list(current.get("recent") or [])
                last_end_by_type = {
                    str(item.get("type")): int(item.get("end_world_minute", -10_000))
                    for item in recent
                }
                eligible = [
                    name for name in allowed
                    if now - int(last_end_by_type.get(name, -10_000)) >= SAME_TYPE_COOLDOWN_MINUTES
                ]
                if not eligible:
                    return transition
                event_type = eligible[int(digest[2]) % len(eligible)]
                event = _start_event(state, event_type, slot, digest)
                current["active"] = event
                current["started_counts"][event_type] = int(current["started_counts"].get(event_type, 0)) + 1
                transition["started"] = dict(event)
    return transition


def active_event(state: dict[str, Any]) -> dict[str, Any] | None:
    current = ensure_situational_events(state)
    active = current.get("active")
    return active if isinstance(active, dict) else None


def _awareness_score(state: dict[str, Any], event: dict[str, Any]) -> float:
    creature = state["creature"]
    score = 0.18 + float(event.get("salience", 0.5)) * 0.58 + float(creature.get("curiosity", 0.5)) * 0.14
    if str(creature.get("zone")) == str(event.get("source_zone")):
        score += 0.16
    if str(creature.get("activity")) == "sleep":
        score -= 0.50
    recent_same = sum(1 for item in ensure_situational_events(state).get("recent", [])[-5:] if item.get("type") == event.get("type"))
    score -= min(0.18, recent_same * 0.055)
    if event.get("type") == "thunder":
        score += 0.18
    return max(0.10, min(0.94, score))


def choose_attention(state: dict[str, Any], event: dict[str, Any]) -> str:
    creature = state["creature"]
    digest = _hash_bytes(event["id"], creature.get("zone"), int(state["tick"]), "attention")
    notice_roll = int(digest[0]) / 255.0
    if notice_roll > _awareness_score(state, event):
        return "ignored"
    response_roll = int(digest[1]) / 255.0
    engage_limit = 0.34 + float(event.get("salience", 0.5)) * 0.30
    if response_roll < engage_limit:
        return "engage"
    return "orient"


def mark_attention(event: dict[str, Any], outcome: str, now: int, *, interrupted_action: str | None = None) -> None:
    if outcome == "ignored":
        event["attention_status"] = "ignored"
        event["outcome"] = "ignored"
        event["response_path"] = list(event.get("response_path") or []) + ["ignored"]
        return
    event["noticed_at"] = int(now)
    if outcome == "orient":
        event["attention_status"] = "oriented"
        event["outcome"] = "oriented"
        event["response_path"] = list(event.get("response_path") or []) + ["orient"]
    elif outcome == "defer":
        event["attention_status"] = "deferred"
        event["response_path"] = list(event.get("response_path") or []) + ["deferred"]
    elif outcome == "interrupt":
        event["attention_status"] = "interrupted"
        event["interrupted_action"] = interrupted_action
        event["response_path"] = list(event.get("response_path") or []) + ["interrupted"]
    else:
        event["attention_status"] = "noticed"
        event["response_path"] = list(event.get("response_path") or []) + ["noticed"]


def mark_engaged(state: dict[str, Any], event: dict[str, Any]) -> None:
    event["attention_status"] = "engaged"
    event["outcome"] = "engaged"
    event["engaged_at"] = int(state["world_minutes"])
    path = list(event.get("response_path") or [])
    if not path or path[-1] != "engaged":
        path.append("engaged")
    event["response_path"] = path


def can_defer_event(state: dict[str, Any], event: dict[str, Any], commitment: dict[str, Any]) -> bool:
    action = str(commitment.get("action") or "")
    if action in {"sleep", "carry", "place", "nudge", "inspect"}:
        return False
    remaining = int(commitment.get("ticks_remaining", 0))
    return remaining > 0 and int(event["end_world_minute"]) - int(state["world_minutes"]) > remaining + 2 and _awareness_score(state, event) >= 0.48


def should_interrupt_event(state: dict[str, Any], event: dict[str, Any], commitment: dict[str, Any]) -> bool:
    action = str(commitment.get("action") or "")
    if action not in {"idle", "rest", "loaf", "groom", "stretch"}:
        return False
    if float(event.get("salience", 0.0)) < 0.84:
        return False
    digest = _hash_bytes(event["id"], action, int(commitment.get("ticks_remaining", 0)), "interrupt")
    return int(digest[0]) / 255.0 < 0.58


def event_frame(state: dict[str, Any]) -> dict[str, Any] | None:
    event = active_event(state)
    if event is None:
        return None
    payload = {
        "id": str(event["id"]),
        "type": str(event["type"]),
        "start_world_minute": int(event["start_world_minute"]),
        "end_world_minute": int(event["end_world_minute"]),
        "salience": float(event["salience"]),
        "source_zone": str(event["source_zone"]),
        "x": int(event.get("x", 0)),
        "y": int(event.get("y", 0)),
        "attention_status": str(event.get("attention_status") or "pending"),
    }
    if event.get("temporary_affordance"):
        payload["temporary_affordance"] = dict(event["temporary_affordance"])
    return payload
