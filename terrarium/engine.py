from __future__ import annotations

import hashlib
import random
import threading
import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .events import make_event, state_patch
from .models import ZONES, clone_state, lighting_for, weather_for
from .store import WorldStore


def _event_timestamp(state: dict[str, Any]) -> str:
    created = datetime.fromisoformat(state["created_at"].replace("Z", "+00:00"))
    stamp = created + timedelta(minutes=int(state["world_minutes"] - 420))
    return stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Simulation:
    """Pure deterministic world transition logic.

    The only entropy source is the PRNG state stored in canonical world state.
    """

    def __init__(self, *, minutes_per_tick: int = 8):
        self.minutes_per_tick = int(minutes_per_tick)

    def _rng(self, state: dict[str, Any]) -> random.Random:
        # Keep host compatibility with Python 3.10. Python 3.12 accepts
        # same-quote expressions inside f-strings (PEP 701); 3.10 does not.
        material = f"{state['seed']}:{state['rules_version']}:{int(state['tick']) + 1}".encode("utf-8")
        tick_seed = int.from_bytes(hashlib.sha256(material).digest()[:16], "big")
        return random.Random(tick_seed)

    @staticmethod
    def _object_in_zone(state: dict[str, Any], zone: str) -> list[dict[str, Any]]:
        return [o for o in state["objects"] if o["zone"] == zone and o["state"] == "placed"]

    def step(self, state: dict[str, Any]) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        before = state
        state = clone_state(state)
        rng = self._rng(before)
        creature = state["creature"]
        habitat = state["habitat"]
        state["tick"] = int(state["tick"]) + 1
        state["world_minutes"] = int(state["world_minutes"]) + self.minutes_per_tick
        habitat["lighting"] = lighting_for(int(state["world_minutes"]))
        habitat["weather"] = weather_for(int(state["world_minutes"]), int(state["seed"]))

        # Drives change slowly. Sleep restores energy; activity spends it.
        if creature["activity"] == "sleep":
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.075)
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.02)
        else:
            creature["energy"] = max(0.0, float(creature["energy"]) - 0.018)
            creature["curiosity"] = min(1.0, float(creature["curiosity"]) + 0.012)

        zone = creature["zone"]
        recent = list(creature.get("recent_actions", []))
        nearby = self._object_in_zone(state, zone)
        carrying = creature.get("carrying")
        lighting = habitat["lighting"]

        candidates: list[tuple[str, float]] = []
        if creature["activity"] == "sleep":
            wake_weight = 0.9 if creature["energy"] >= 0.86 or lighting in {"dawn", "day"} else 0.08
            candidates.extend([("wake", wake_weight), ("sleep", 1.0)])
        else:
            if float(creature["energy"]) < 0.26 or (lighting == "night" and float(creature["energy"]) < 0.58):
                candidates.append(("sleep", 1.5))
            candidates.extend(
                [
                    ("idle", 0.33),
                    ("rest", 0.45 + (1.0 - float(creature["energy"])) * 0.45),
                    ("walk", 0.66),
                    ("explore", 0.50 + float(creature["curiosity"]) * 0.30),
                ]
            )
            if zone == "window":
                candidates.append(("look_outside", 0.78 + (0.22 if habitat["weather"] != "clear" else 0.0)))
            if nearby and not carrying:
                candidates.append(("inspect", 0.72 + float(creature["curiosity"]) * 0.24))
                candidates.append(("carry", 0.36 + float(creature["curiosity"]) * 0.18))
            if carrying:
                candidates.append(("place", 1.15 if zone == "collection_shelf" else 0.55))
                candidates.append(("walk", 1.0))

        # Cool down obvious loops while still allowing sustained sleep.
        adjusted: list[tuple[str, float]] = []
        for action, weight in candidates:
            repeats = sum(1 for a in recent[-4:] if a == action)
            penalty = 1.0 if action == "sleep" else 0.46 ** repeats
            adjusted.append((action, max(0.015, weight * penalty)))
        total = sum(w for _, w in adjusted)
        pick = rng.random() * total
        action = adjusted[-1][0]
        cursor = 0.0
        for name, weight in adjusted:
            cursor += weight
            if pick <= cursor:
                action = name
                break

        details: dict[str, Any] = {"from_zone": zone, "lighting": lighting, "weather": habitat["weather"]}
        event_type = "creature_activity"
        summary = "Moss is quietly awake."

        if action in {"walk", "explore"}:
            options = [z for z in ZONES if z != zone]
            if carrying and "collection_shelf" in options:
                options.extend(["collection_shelf", "collection_shelf"])
            target = rng.choice(options)
            old_x = int(creature["x"])
            creature["zone"] = target
            creature["x"] = int(ZONES[target]["x"])
            creature["y"] = int(ZONES[target]["y"])
            creature["facing"] = "right" if creature["x"] >= old_x else "left"
            creature["activity"] = "walk"
            creature["expression"] = "curious" if action == "explore" else "neutral"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - (0.045 if action == "explore" else 0.018))
            habitat["path_wear"][target] = int(habitat["path_wear"].get(target, 0)) + 1
            if habitat["path_wear"][target] in {6, 14}:
                mark = f"worn_{target}_{habitat['path_wear'][target]}"
                if mark not in habitat["marks"]:
                    habitat["marks"].append(mark)
            if carrying:
                carried = next(o for o in state["objects"] if o["id"] == carrying)
                carried["zone"] = target
                carried["x"] = creature["x"] + (-14 if creature["facing"] == "left" else 14)
                carried["y"] = creature["y"] - 22
            details["to_zone"] = target
            event_type = "creature_moved"
            summary = f"Moss wandered from {zone.replace('_', ' ')} to {target.replace('_', ' ')}."
        elif action == "inspect" and nearby:
            obj = rng.choice(nearby)
            obj["times_inspected"] = int(obj["times_inspected"]) + 1
            creature["activity"] = "inspect"
            creature["expression"] = "curious"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.09)
            details["object_id"] = obj["id"]
            event_type = "object_inspected"
            summary = f"Moss stopped to inspect the {obj['name'].lower()}."
        elif action == "carry" and nearby:
            obj = rng.choice(nearby)
            creature["carrying"] = obj["id"]
            creature["activity"] = "carry"
            creature["expression"] = "excited"
            obj["state"] = "carried"
            obj["carried_by"] = creature["id"]
            obj["x"] = int(creature["x"]) + 14
            obj["y"] = int(creature["y"]) - 22
            details["object_id"] = obj["id"]
            event_type = "object_picked_up"
            summary = f"Moss picked up the {obj['name'].lower()}."
        elif action == "place" and carrying:
            obj = next(o for o in state["objects"] if o["id"] == carrying)
            obj["state"] = "placed"
            obj["carried_by"] = None
            obj["zone"] = zone
            if zone == "collection_shelf":
                shelf_items = [o for o in state["objects"] if o["zone"] == zone and o["state"] == "placed" and o["id"] != obj["id"]]
                obj["x"] = 632 + 28 * (len(shelf_items) % 4)
                obj["y"] = 184 - 27 * (len(shelf_items) // 4)
            else:
                obj["x"] = max(42, min(758, int(creature["x"]) + rng.randint(-34, 34)))
                obj["y"] = max(88, min(420, int(creature["y"]) + rng.randint(18, 34)))
            obj["times_moved"] = int(obj["times_moved"]) + 1
            creature["carrying"] = None
            creature["activity"] = "place"
            creature["expression"] = "content"
            details.update({"object_id": obj["id"], "to_zone": zone, "x": obj["x"], "y": obj["y"]})
            event_type = "object_placed"
            summary = f"Moss placed the {obj['name'].lower()} in the {zone.replace('_', ' ')}."
        elif action == "sleep":
            if zone != "sleeping_nook" and float(creature["energy"]) < 0.18:
                creature["zone"] = "sleeping_nook"
                creature["x"] = ZONES["sleeping_nook"]["x"]
                creature["y"] = ZONES["sleeping_nook"]["y"]
            creature["activity"] = "sleep"
            creature["expression"] = "sleepy"
            event_type = "creature_slept"
            summary = f"Moss fell asleep in the {creature['zone'].replace('_', ' ')}."
        elif action == "wake":
            creature["activity"] = "idle"
            creature["expression"] = "content"
            event_type = "creature_woke"
            summary = "Moss woke up and looked around."
        elif action == "rest":
            creature["activity"] = "rest"
            creature["expression"] = "content"
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.034)
            event_type = "creature_rested"
            summary = f"Moss rested for a while in the {zone.replace('_', ' ')}."
        elif action == "look_outside":
            creature["activity"] = "look_outside"
            creature["expression"] = "content" if habitat["weather"] == "rain" else "curious"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.055)
            event_type = "window_watched"
            summary = f"Moss watched the {habitat['weather']} outside the window."
        else:
            creature["activity"] = "idle"
            creature["expression"] = "neutral"
            event_type = "creature_idled"
            summary = f"Moss lingered in the {zone.replace('_', ' ')}."

        creature["recent_actions"] = (recent + [action])[-8:]
        habitat["shelf_count"] = sum(1 for o in state["objects"] if o["zone"] == "collection_shelf" and o["state"] == "placed")
        details["action"] = action
        details["energy_after"] = round(float(creature["energy"]), 6)
        return event_type, summary, details, state


class WorldEngine:
    def __init__(self, store: WorldStore, *, seed: int = 1701, minutes_per_tick: int = 8, snapshot_every: int = 20):
        self.store = store
        self.state = store.initialize(seed)
        self.simulation = Simulation(minutes_per_tick=minutes_per_tick)
        self.snapshot_every = int(snapshot_every)
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def step(self) -> dict[str, Any]:
        with self._lock:
            before = self.state
            event_type, summary, details, next_state = self.simulation.step(before)
            last = self.store.last_event()
            seq = int(last["seq"]) + 1 if last else 1
            prev_hash = str(last["content_hash"]) if last else "0" * 64
            event = make_event(
                seq=seq,
                tick=int(next_state["tick"]),
                event_type=event_type,
                actor="creature-1",
                summary=summary,
                details=details,
                effects=state_patch(before, next_state),
                prev_hash=prev_hash,
                timestamp=_event_timestamp(next_state),
            )
            self.store.append_event(event, state_after=next_state, snapshot_every=self.snapshot_every)
            self.state = next_state
            return event

    def run_steps(self, count: int) -> list[dict[str, Any]]:
        return [self.step() for _ in range(int(count))]

    def start(self, *, tick_seconds: float = 3.0) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()

        def loop() -> None:
            while not self._stop.wait(tick_seconds):
                self.step()

        self._thread = threading.Thread(target=loop, name="terrarium-world", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def current_state(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self.state)
