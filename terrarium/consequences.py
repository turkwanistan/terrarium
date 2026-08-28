from __future__ import annotations

import hashlib
from typing import Any

from .models import CONSEQUENCE_MEMORY_SCHEMA, ZONES, object_affordances

# Hot causal state is deliberately small. The append-only event ledger remains
# the complete historical record; this index only keeps unresolved consequences
# that are still capable of becoming a later opportunity.
CONSEQUENCE_MEMORY_LIMIT = 12
CONSEQUENCE_MIN_DELAY_MINUTES = 45
CONSEQUENCE_MAX_AGE_MINUTES = 4320


_RETENTION_KIND_BONUS = {
    "persistent_trace": 0.16,
    "situational_aftermath": 0.10,
    "object_displacement": 0.08,
    "object_nest": 0.10,
    "object_arrangement": 0.00,
}


def _retain_entries(entries: list[dict[str, Any]], now: int) -> list[dict[str, Any]]:
    """Bound hot memory by causal significance rather than blind FIFO eviction."""
    if len(entries) <= CONSEQUENCE_MEMORY_LIMIT:
        return entries
    def score(entry: dict[str, Any]) -> tuple[float, int, str]:
        eligible = int(entry.get("created_world_minute", now)) + int(entry.get("delay_minutes", CONSEQUENCE_MIN_DELAY_MINUTES))
        value = float(entry.get("strength", 0.5))
        value += min(0.18, max(0, int(entry.get("source_count", 1)) - 1) * 0.04)
        value += _RETENTION_KIND_BONUS.get(str(entry.get("kind") or ""), 0.04)
        if now >= eligible:
            value += 0.04
        return (round(value, 6), int(entry.get("created_world_minute", 0)), str(entry.get("id") or ""))
    kept = sorted(entries, key=score, reverse=True)[:CONSEQUENCE_MEMORY_LIMIT]
    return sorted(kept, key=lambda entry: (int(entry.get("created_world_minute", 0)), str(entry.get("id") or "")))

_SOURCE_DETAIL_KEYS = (
    "world_event_id",
    "world_event_type",
    "world_event_outcome",
    "object_affordance",
    "object_state",
    "mark",
    "wear_count",
)


def _memory_id(state: dict[str, Any], kind: str, subject: str) -> str:
    material = f"{int(state['seed'])}:{int(state['tick'])}:{int(state['world_minutes'])}:{kind}:{subject}".encode("utf-8")
    return "con-" + hashlib.sha256(material).hexdigest()[:16]


def _source_payload(state: dict[str, Any], source: dict[str, Any] | None) -> dict[str, Any]:
    """Keep enough provenance/context to explain the hot index without copying history."""
    raw = dict(source or {})
    seasonal = state["habitat"].get("seasonal_clock") or {}
    payload: dict[str, Any] = {
        "cause": str(raw.get("cause") or "world_consequence"),
        "tick": int(state["tick"]),
        "weather": str(state["habitat"].get("weather") or "clear"),
        "season": seasonal.get("season"),
    }
    for key in _SOURCE_DETAIL_KEYS:
        value = raw.get(key)
        if value is not None:
            payload[key] = value
    return payload


def ensure_consequence_memory(state: dict[str, Any]) -> dict[str, Any]:
    habitat = state["habitat"]
    current = habitat.get("consequence_memory")
    if not isinstance(current, dict) or current.get("schema") != CONSEQUENCE_MEMORY_SCHEMA:
        current = {
            "schema": CONSEQUENCE_MEMORY_SCHEMA,
            "migration_origin": "neutral-existing-world",
            "entries": [],
            "created_count": 0,
            "revisit_count": 0,
            "resolved_count": 0,
        }
        habitat["consequence_memory"] = current
    current["schema"] = CONSEQUENCE_MEMORY_SCHEMA
    current.setdefault("migration_origin", "native")
    current["created_count"] = max(0, int(current.get("created_count", 0)))
    current["revisit_count"] = max(0, int(current.get("revisit_count", 0)))
    current["resolved_count"] = max(0, int(current.get("resolved_count", 0)))
    cleaned: list[dict[str, Any]] = []
    for raw in list(current.get("entries") or []):
        if not isinstance(raw, dict):
            continue
        zone = str(raw.get("zone") or "")
        if zone not in ZONES:
            continue
        entry = {
            "id": str(raw.get("id") or ""),
            "kind": str(raw.get("kind") or "aftermath"),
            "zone": zone,
            "object_id": str(raw.get("object_id")) if raw.get("object_id") else None,
            "created_world_minute": int(raw.get("created_world_minute", state.get("world_minutes", 0))),
            "delay_minutes": max(1, int(raw.get("delay_minutes", raw.get("eligible_after_world_minute", state.get("world_minutes", 0)) - int(raw.get("created_world_minute", state.get("world_minutes", 0))) or CONSEQUENCE_MIN_DELAY_MINUTES))),
            "strength": round(max(0.1, min(1.0, float(raw.get("strength", 0.5)))), 6),
            "source_count": max(1, int(raw.get("source_count", 1))),
            "source": dict(raw.get("source") or {}),
        }
        if raw.get("resolved"):
            entry["resolved"] = True
        if raw.get("revisits"):
            entry["revisits"] = max(0, int(raw.get("revisits", 0)))
        if entry["id"]:
            cleaned.append(entry)
    current["entries"] = _retain_entries(cleaned, int(state.get("world_minutes", 0)))
    return current


def prune_consequence_memory(state: dict[str, Any]) -> dict[str, Any]:
    current = ensure_consequence_memory(state)
    now = int(state["world_minutes"])
    current["entries"] = _retain_entries([
        entry for entry in current["entries"]
        if not bool(entry.get("resolved"))
        and now <= int(entry["created_world_minute"]) + CONSEQUENCE_MAX_AGE_MINUTES
    ], now)
    return current


def record_consequence(
    state: dict[str, Any],
    *,
    kind: str,
    zone: str,
    object_id: str | None = None,
    strength: float = 0.55,
    source: dict[str, Any] | None = None,
    min_delay_minutes: int = CONSEQUENCE_MIN_DELAY_MINUTES,
) -> dict[str, Any]:
    current = prune_consequence_memory(state)
    now = int(state["world_minutes"])
    zone = str(zone)
    if zone not in ZONES:
        raise ValueError(f"unknown consequence zone: {zone}")
    subject = str(object_id or zone)
    merge_key = (str(kind), str(object_id or ""), zone)
    existing = next(
        (
            entry for entry in reversed(current["entries"])
            if (str(entry.get("kind")), str(entry.get("object_id") or ""), str(entry.get("zone"))) == merge_key
            and not bool(entry.get("resolved"))
        ),
        None,
    )
    payload = _source_payload(state, source)
    if existing is not None:
        existing["strength"] = round(min(1.0, max(float(existing.get("strength", 0.5)), float(strength)) + 0.06), 6)
        existing["source_count"] = int(existing.get("source_count", 1)) + 1
        existing["delay_minutes"] = min(int(existing.get("delay_minutes", CONSEQUENCE_MIN_DELAY_MINUTES)), max(1, int(min_delay_minutes)))
        existing["source"] = payload
        return existing
    entry = {
        "id": _memory_id(state, str(kind), subject),
        "kind": str(kind),
        "zone": zone,
        "object_id": str(object_id) if object_id else None,
        "created_world_minute": now,
        "delay_minutes": max(1, int(min_delay_minutes)),
        "strength": round(max(0.1, min(1.0, float(strength))), 6),
        "source_count": 1,
        "source": payload,
    }
    current["entries"] = _retain_entries(current["entries"] + [entry], now)
    current["created_count"] = int(current["created_count"]) + 1
    return entry


def _relative_zone_habit(state: dict[str, Any], zone: str) -> float:
    profile = state["creature"].get("habit_profile") or {}
    values = profile.get("zone_affinity") or {}
    if not values or zone not in values:
        return 0.0
    mean = sum(float(v) for v in values.values()) / max(1, len(values))
    return max(-0.25, min(0.35, float(values.get(zone, 0.0)) - mean))


def _entry_action(state: dict[str, Any], entry: dict[str, Any]) -> tuple[str, str | None] | None:
    object_id = entry.get("object_id")
    if object_id:
        obj = next((item for item in state["objects"] if str(item["id"]) == str(object_id)), None)
        if obj is not None and obj.get("state") == "placed" and str(obj.get("zone")) == str(entry["zone"]):
            if "inspect" in object_affordances(obj):
                return "inspect", str(object_id)
    zone = str(entry["zone"])
    if zone == "window":
        return "look_outside", None
    if zone != "collection_shelf":
        return "loaf", None
    return "rest", None


def consequence_opportunities(state: dict[str, Any]) -> list[dict[str, Any]]:
    current = prune_consequence_memory(state)
    now = int(state["world_minutes"])
    seasonal = state["habitat"].get("seasonal_clock") or {}
    weather = str(state["habitat"].get("weather") or "clear")
    season = seasonal.get("season")
    opportunities: list[dict[str, Any]] = []
    for entry in current["entries"]:
        eligible = int(entry["created_world_minute"]) + int(entry.get("delay_minutes", CONSEQUENCE_MIN_DELAY_MINUTES))
        if now < eligible:
            continue
        action = _entry_action(state, entry)
        if action is None:
            continue
        engage_action, object_id = action
        age = max(0, now - int(entry["created_world_minute"]))
        age_factor = min(1.0, age / 720.0)
        source = entry.get("source") or {}
        context_bonus = 0.0
        if source.get("weather") == weather:
            context_bonus += 0.08
        if source.get("season") and source.get("season") == season:
            context_bonus += 0.05
        habit_bonus = max(-0.08, min(0.16, _relative_zone_habit(state, str(entry["zone"])) * 0.45))
        aftermath = state["habitat"].get("affordance_history") or {}
        arrangements = int((aftermath.get("zone_arrangements") or {}).get(str(entry["zone"]), 0))
        comfort = int((aftermath.get("zone_comfort") or {}).get(str(entry["zone"]), 0))
        trace_bonus = min(0.12, (arrangements + comfort) * 0.003)
        score = max(0.08, min(1.25, 0.14 + float(entry["strength"]) * 0.42 + age_factor * 0.16 + context_bonus + habit_bonus + trace_bonus))
        opportunities.append({
            "memory_id": str(entry["id"]),
            "kind": str(entry["kind"]),
            "zone": str(entry["zone"]),
            "object_id": object_id,
            "engage_action": engage_action,
            "score": round(score, 6),
            "age_minutes": age,
            "source": dict(source),
        })
    opportunities.sort(key=lambda item: (-float(item["score"]), -int(item["age_minutes"]), str(item["memory_id"])))
    return opportunities


def find_consequence(state: dict[str, Any], memory_id: str) -> dict[str, Any] | None:
    current = ensure_consequence_memory(state)
    return next((entry for entry in current["entries"] if str(entry.get("id")) == str(memory_id)), None)


def mark_consequence_revisited(state: dict[str, Any], memory_id: str) -> dict[str, Any] | None:
    current = ensure_consequence_memory(state)
    entry = find_consequence(state, memory_id)
    if entry is None:
        return None
    # One unresolved consequence produces at most one later revisit. Repeated
    # causal sources reinforce/merge before that revisit instead of creating a
    # permanent loop. The resolved entry survives this tick for event provenance
    # and is pruned on the next ordinary world step.
    entry["revisits"] = 1
    entry["resolved"] = True
    current["revisit_count"] = int(current["revisit_count"]) + 1
    current["resolved_count"] = int(current["resolved_count"]) + 1
    return entry
