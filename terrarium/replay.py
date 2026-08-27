from __future__ import annotations

import json
from typing import Any

from .events import apply_patch, verify_event
from .models import canonical_json, sha256_json
from .store import WorldStore


def reconstruct(store: WorldStore, *, through_seq: int | None = None) -> dict[str, Any]:
    snapshot = store.latest_snapshot(through_seq=through_seq)
    state = json.loads(snapshot["state_json"])
    if sha256_json(state) != snapshot["state_hash"]:
        raise ValueError("snapshot hash mismatch")
    snap_seq = int(snapshot["seq"])
    if snap_seq == 0:
        prev_hash = "0" * 64
    else:
        prior = list(store.iter_events(after_seq=snap_seq - 1, through_seq=snap_seq))
        if len(prior) != 1:
            raise ValueError("snapshot event anchor missing")
        verify_event(prior[0])
        prev_hash = prior[0]["content_hash"]
    for event in store.iter_events(after_seq=snap_seq, through_seq=through_seq):
        verify_event(event, expected_prev_hash=prev_hash)
        state = apply_patch(state, event["effects"])
        prev_hash = event["content_hash"]
    return state


def assert_exact_replay(store: WorldStore) -> dict[str, Any]:
    replayed = reconstruct(store)
    current = store.load_state()
    if current is None:
        raise ValueError("canonical state missing")
    ok = canonical_json(replayed) == canonical_json(current)
    return {
        "ok": ok,
        "event_count": store.event_count(),
        "replayed_state_hash": sha256_json(replayed),
        "canonical_state_hash": sha256_json(current),
    }
