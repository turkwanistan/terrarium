from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from .models import EVENT_VERSION, canonical_json, sha256_json, utc_now

EVENT_SCHEMA = "terrarium.event.v1"


def state_patch(before: Any, after: Any, path: list[Any] | None = None) -> list[dict[str, Any]]:
    """Return deterministic compact replacements needed to turn before into after."""
    path = [] if path is None else path
    if type(before) is not type(after):
        return [{"path": path, "value": deepcopy(after)}]
    if isinstance(before, dict):
        if set(before) != set(after):
            return [{"path": path, "value": deepcopy(after)}]
        out: list[dict[str, Any]] = []
        for key in sorted(before):
            out.extend(state_patch(before[key], after[key], path + [key]))
        return out
    if isinstance(before, list):
        if len(before) != len(after):
            return [{"path": path, "value": deepcopy(after)}]
        out: list[dict[str, Any]] = []
        for index, (left, right) in enumerate(zip(before, after)):
            out.extend(state_patch(left, right, path + [index]))
        return out
    if before != after:
        return [{"path": path, "value": deepcopy(after)}]
    return []


def apply_patch(state: dict[str, Any], patch: list[dict[str, Any]]) -> dict[str, Any]:
    out = deepcopy(state)
    for op in patch:
        path = op.get("path")
        if not isinstance(path, list) or not path:
            if path == [] and isinstance(op.get("value"), dict):
                out = deepcopy(op["value"])
                continue
            raise ValueError("invalid state patch path")
        cursor: Any = out
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = deepcopy(op["value"])
    return out


def make_event(
    *,
    seq: int,
    tick: int,
    event_type: str,
    actor: str,
    summary: str,
    details: dict[str, Any],
    effects: list[dict[str, Any]],
    prev_hash: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    event = {
        "schema": EVENT_SCHEMA,
        "event_version": EVENT_VERSION,
        "event_id": f"evt_{seq:09d}",
        "seq": seq,
        "tick": tick,
        "timestamp": timestamp or utc_now(),
        "type": event_type,
        "actor": actor,
        "summary": summary,
        "details": details,
        "effects": effects,
        "prev_hash": prev_hash,
    }
    event["content_hash"] = sha256_json(event)
    return event


def verify_event(event: dict[str, Any], *, expected_prev_hash: str | None = None) -> None:
    if event.get("schema") != EVENT_SCHEMA:
        raise ValueError("unsupported event schema")
    declared = event.get("content_hash")
    material = {k: v for k, v in event.items() if k != "content_hash"}
    if declared != sha256_json(material):
        raise ValueError(f"event content hash mismatch: {event.get('event_id')}")
    if expected_prev_hash is not None and event.get("prev_hash") != expected_prev_hash:
        raise ValueError(f"event chain mismatch: {event.get('event_id')}")
    if not isinstance(event.get("effects"), list):
        raise ValueError("event effects must be a state patch")


def verify_chain(events: Iterable[dict[str, Any]], *, initial_hash: str = "0" * 64) -> str:
    prev = initial_hash
    expected_seq: int | None = None
    for event in events:
        verify_event(event, expected_prev_hash=prev)
        seq = int(event["seq"])
        if expected_seq is not None and seq != expected_seq:
            raise ValueError(f"event sequence gap: expected {expected_seq}, got {seq}")
        expected_seq = seq + 1
        prev = str(event["content_hash"])
    return prev


def event_line(event: dict[str, Any]) -> str:
    return canonical_json(event) + "\n"
