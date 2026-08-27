from __future__ import annotations

import hashlib
import random
import threading
import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .events import make_event, state_patch
from .models import BEHAVIOR_CONTEXT_SCHEMA, PLACEMENT_SLOTS, RULES_VERSION, ZONES, clone_state, lighting_for, weather_for
from .spatial import (
    SLEEP_SUPPORT_ANCHOR, SPATIAL_SCHEMA, interaction_approach, interaction_contact, route_between,
    route_length, route_payload, zone_anchor,
)
from .store import WorldStore


def _event_timestamp(state: dict[str, Any]) -> str:
    created = datetime.fromisoformat(state["created_at"].replace("Z", "+00:00"))
    stamp = created + timedelta(minutes=int(state["world_minutes"] - 420))
    return stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Simulation:
    # Number of continuation ticks after the decision tick. The world still
    # advances every three-second heartbeat, but visible intent is allowed to
    # persist long enough to read as acting rather than constant resampling.
    COMMITMENT_TICKS = {
        "idle": 2, "rest": 3, "walk": 1, "explore": 1, "inspect": 2,
        "carry": 1, "place": 2, "look_outside": 5, "sleep": 6, "wake": 2,
    }

    """Pure deterministic world transition logic.

    The only entropy source is the PRNG state stored in canonical world state.
    """

    def __init__(self, *, minutes_per_tick: int = 1):
        self.minutes_per_tick = int(minutes_per_tick)

    def _rng(self, state: dict[str, Any]) -> random.Random:
        # Keep host compatibility with Python 3.10. Python 3.12 accepts
        # same-quote expressions inside f-strings (PEP 701); 3.10 does not.
        material = f"{state['seed']}:{state['rules_version']}:{int(state['tick']) + 1}".encode("utf-8")
        tick_seed = int.from_bytes(hashlib.sha256(material).digest()[:16], "big")
        return random.Random(tick_seed)

    @staticmethod
    def _behavior_context(creature: dict[str, Any]) -> dict[str, Any]:
        """Return the small bounded routine context, migrating legacy worlds in-place.

        Canonical event history remains the long-term record.  This hot state only
        remembers enough recent behavior to make the next choice context-aware.
        """
        context = creature.setdefault(
            "behavior_context",
            {
                "schema": BEHAVIOR_CONTEXT_SCHEMA,
                "recent_zones": [str(creature.get("zone", "open_space"))],
                "recent_objects": [],
                "intent": None,
            },
        )
        context["schema"] = BEHAVIOR_CONTEXT_SCHEMA
        recent_zones = [str(z) for z in context.get("recent_zones", []) if str(z) in ZONES][-4:]
        if not recent_zones:
            recent_zones = [str(creature.get("zone", "open_space"))]
        context["recent_zones"] = recent_zones
        recent_objects: list[str] = []
        for value in context.get("recent_objects", []):
            object_id = str(value) if value else ""
            if object_id and object_id not in recent_objects:
                recent_objects.append(object_id)
        context["recent_objects"] = recent_objects[-4:]
        intent = context.get("intent")
        if intent is not None and not isinstance(intent, dict):
            context["intent"] = None
        return context

    @staticmethod
    def _remember_zone(context: dict[str, Any], zone: str) -> None:
        recent = [str(z) for z in context.get("recent_zones", []) if str(z) in ZONES]
        context["recent_zones"] = (recent + [str(zone)])[-4:]

    @staticmethod
    def _remember_object(context: dict[str, Any], object_id: str) -> None:
        recent = [str(o) for o in context.get("recent_objects", []) if o and str(o) != str(object_id)]
        context["recent_objects"] = (recent + [str(object_id)])[-4:]

    @staticmethod
    def _weighted_pick(rng: random.Random, weighted: list[tuple[str, float]]) -> str:
        total = sum(max(0.0, float(weight)) for _, weight in weighted)
        if total <= 0.0:
            return weighted[-1][0]
        pick = rng.random() * total
        cursor = 0.0
        for name, weight in weighted:
            cursor += max(0.0, float(weight))
            if pick <= cursor:
                return name
        return weighted[-1][0]

    def _choose_object(
        self,
        rng: random.Random,
        nearby: list[dict[str, Any]],
        context: dict[str, Any],
        *,
        preferred_id: str | None = None,
    ) -> dict[str, Any]:
        if preferred_id:
            preferred = next((o for o in nearby if o["id"] == preferred_id and o["state"] == "placed"), None)
            if preferred is not None:
                return preferred
        recent = list(context.get("recent_objects", []))
        weighted: list[tuple[str, float]] = []
        by_id = {str(o["id"]): o for o in nearby}
        last_object_id = recent[-1] if recent else None
        alternatives_exist = bool(last_object_id) and any(str(o["id"]) != last_object_id for o in nearby)
        for obj in nearby:
            object_id = str(obj["id"])
            # A completed object session gets a short, deterministic "done with
            # this for now" inhibition whenever another local object exists.
            if alternatives_exist and object_id == last_object_id:
                continue
            weight = 1.0 / (1.0 + 0.12 * int(obj.get("times_inspected", 0)))
            if object_id in recent[-4:]:
                weight *= 0.42
            weighted.append((object_id, max(0.01, weight)))
        return by_id[self._weighted_pick(rng, weighted)]

    def _choose_destination(
        self,
        rng: random.Random,
        state: dict[str, Any],
        context: dict[str, Any],
        *,
        zone: str,
        carrying: str | None,
    ) -> str:
        """Choose travel as a consequence of context instead of a uniform room hop."""
        intent = dict(context.get("intent") or {})
        if carrying:
            target_zone = str(intent.get("target_zone") or "")
            if target_zone in ZONES and target_zone != zone:
                return target_zone
        recent = list(context.get("recent_zones", []))
        energy = float(state["creature"]["energy"])
        curiosity = float(state["creature"]["curiosity"])
        weather = str(state["habitat"]["weather"])
        weighted: list[tuple[str, float]] = []
        for target in ZONES:
            if target == zone:
                continue
            weight = 1.0
            # The zone immediately before the current one is the clearest
            # ping-pong signal; older recent zones are only mildly inhibited.
            if len(recent) >= 2 and target == recent[-2]:
                weight *= 0.12
            elif target in recent[-4:]:
                weight *= 0.48

            if carrying:
                if target == "collection_shelf":
                    weight *= 9.0
                elif target == "open_space":
                    weight *= 0.72
                else:
                    weight *= 0.42
            else:
                if target == "open_space":
                    weight *= 1.30
                if target == "window":
                    weight *= 1.18 + (0.32 if weather != "clear" else 0.0)
                if target == "activity_corner":
                    weight *= 1.0 + 0.45 * curiosity
                if target == "sleeping_nook" and energy < 0.48:
                    weight *= 1.0 + (0.48 - energy) * 4.0
            weighted.append((target, max(0.01, weight)))
        return self._weighted_pick(rng, weighted)

    @staticmethod
    def _object_in_zone(state: dict[str, Any], zone: str) -> list[dict[str, Any]]:
        return [o for o in state["objects"] if o["zone"] == zone and o["state"] == "placed"]

    @staticmethod
    def _route_creature(
        creature: dict[str, Any],
        details: dict[str, Any],
        *,
        destination: tuple[int, int],
        destination_zone: str,
    ) -> list[tuple[int, int]]:
        """Move canonical state to an authored physical endpoint and record its route."""
        source = (int(creature["x"]), int(creature["y"]))
        source_zone = str(creature["zone"])
        route = route_between(source, source_zone, destination, destination_zone)
        details.update({
            "spatial_schema": SPATIAL_SCHEMA,
            "source_x": source[0], "source_y": source[1],
            "approach_x": int(destination[0]), "approach_y": int(destination[1]),
            "route": route_payload(source, route),
            "route_length": round(route_length(source, route), 6),
        })
        prior = source
        for current in route:
            if current[0] != prior[0]:
                creature["facing"] = "right" if current[0] > prior[0] else "left"
            prior = current
        creature["zone"] = destination_zone
        creature["x"], creature["y"] = int(destination[0]), int(destination[1])
        return route

    @staticmethod
    def _placement_position(state: dict[str, Any], obj: dict[str, Any], zone: str) -> tuple[int, int]:
        """Choose a deterministic authored staging point for a placed object.

        Repeated autonomous life should gradually create arrangements that look
        habitat-aware rather than like random coordinate scatter. Existing
        placed objects reserve nearby slots so small collections stay legible.
        """
        slots = PLACEMENT_SLOTS[zone]
        material = f"{obj['id']}:{zone}:{int(obj['times_moved']) + 1}".encode("utf-8")
        start = int.from_bytes(hashlib.sha256(material).digest()[:2], "big") % len(slots)
        occupied = [
            (int(other["x"]), int(other["y"]))
            for other in state["objects"]
            if other["id"] != obj["id"] and other["state"] == "placed" and other["zone"] == zone
        ]
        for offset in range(len(slots)):
            x, y = slots[(start + offset) % len(slots)]
            if all((x - ox) ** 2 + (y - oy) ** 2 >= 20 ** 2 for ox, oy in occupied):
                return x, y
        return slots[start]

    def _continue_committed_action(self, state: dict[str, Any]) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        creature = state["creature"]
        habitat = state["habitat"]
        commitment = dict(creature.get("behavior_commitment") or {})
        intent = str(commitment.get("action") or "idle")
        remaining = max(0, int(commitment.get("ticks_remaining", 0)) - 1)
        object_id = commitment.get("object_id")
        commitment["ticks_remaining"] = remaining
        creature["behavior_commitment"] = commitment
        creature["focus_object_id"] = object_id

        # Locomotion/wake recover into a quiet planted stance. Manipulation and
        # observation hold their readable contact pose for the commitment.
        visible = "idle" if intent in {"walk", "explore"} or (intent == "wake" and remaining == 0) else intent
        if visible == "sleep":
            creature["activity"] = "sleep"
            creature["expression"] = "sleepy"
        elif visible == "wake":
            creature["activity"] = "wake"
            creature["expression"] = "content"
        elif visible == "rest":
            creature["activity"] = "rest"
            creature["expression"] = "content"
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.034)
        elif visible == "look_outside":
            creature["activity"] = "look_outside"
            creature["expression"] = "content" if habitat["weather"] == "rain" else "curious"
        elif visible == "inspect":
            creature["activity"] = "inspect"
            creature["expression"] = "curious"
        elif visible == "carry":
            creature["activity"] = "carry"
            creature["expression"] = "content"
        elif visible == "place":
            creature["activity"] = "place"
            creature["expression"] = "content"
        else:
            creature["activity"] = "idle"
            creature["expression"] = "content" if intent in {"walk", "explore", "wake"} else "neutral"

        details: dict[str, Any] = {
            "from_zone": creature["zone"],
            "lighting": habitat["lighting"],
            "weather": habitat["weather"],
            "action": visible,
            "intent_action": intent,
            "decision": False,
            "commitment_ticks_remaining": remaining,
        }
        if object_id:
            details["object_id"] = object_id
            obj = next((o for o in state["objects"] if o["id"] == object_id), None)
            if obj is not None:
                details["target_x"] = int(obj["x"])
                details["target_y"] = int(obj["y"])
                contact = interaction_contact(
                    zone=str(creature["zone"]), target_x=int(obj["x"]), target_y=int(obj["y"]),
                    approach=(int(creature["x"]), int(creature["y"])),
                )
                details["contact_x"], details["contact_y"] = contact
        if intent == "wake" and remaining == 0:
            support = (int(SLEEP_SUPPORT_ANCHOR["x"]), int(SLEEP_SUPPORT_ANCHOR["y"]))
            if (int(creature["x"]), int(creature["y"])) == support:
                self._route_creature(creature, details, destination=zone_anchor("sleeping_nook"), destination_zone="sleeping_nook")
                details["supported_action"] = "wake_exit"
        summary = {
            "sleep": "Moss remained curled up asleep.",
            "wake": "Moss stayed near the bed, finishing a slow wake-up stretch.",
            "rest": "Moss stayed settled and rested quietly.",
            "look_outside": "Moss kept watching the world beyond the window.",
            "inspect": "Moss lingered over the object, still studying it.",
            "carry": "Moss steadied the object against its chest before moving on.",
            "place": "Moss let the placed object settle before pulling back.",
            "idle": "Moss paused, planted and quiet, before choosing what to do next.",
        }.get(visible, "Moss stayed with the current activity.")
        return "creature_activity", summary, details, state

    def step(self, state: dict[str, Any]) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        before = state
        state = clone_state(state)
        # Existing canonical worlds migrate forward through an ordinary hashed
        # state patch on their next tick; snapshots/events remain replayable.
        state["rules_version"] = RULES_VERSION
        rng = self._rng(before)
        creature = state["creature"]
        creature.setdefault("focus_object_id", None)
        creature.setdefault("behavior_commitment", {"action": None, "ticks_remaining": 0, "object_id": None})
        context = self._behavior_context(creature)
        if creature.get("carrying") and not context.get("intent"):
            # Legacy/live worlds may upgrade while Moss is already holding an
            # object.  Continue that possession through normal state evolution
            # instead of resetting it or leaving the new routine context empty.
            legacy_target = "collection_shelf" if creature.get("zone") != "collection_shelf" else "open_space"
            context["intent"] = {
                "kind": "object_session",
                "stage": "carrying",
                "object_id": creature.get("carrying"),
                "target_zone": legacy_target,
            }
        habitat = state["habitat"]
        aftermath = habitat.setdefault(
            "activity_aftermath",
            {
                "sleep_nook_ticks": 0,
                "sleep_nook_bouts": 0,
                "window_watches": 0,
                "wet_window_watches": 0,
                "activity_corner_uses": 0,
            },
        )
        for key in ("sleep_nook_ticks", "sleep_nook_bouts", "window_watches", "wet_window_watches", "activity_corner_uses"):
            aftermath.setdefault(key, 0)
        state["tick"] = int(state["tick"]) + 1
        state["world_minutes"] = int(state["world_minutes"]) + self.minutes_per_tick
        habitat["lighting"] = lighting_for(int(state["world_minutes"]))
        habitat["weather"] = weather_for(int(state["world_minutes"]), int(state["seed"]))

        # Drives change every heartbeat even when a behavioral intent is held.
        if creature["activity"] == "sleep":
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.075)
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.02)
        else:
            creature["energy"] = max(0.0, float(creature["energy"]) - 0.018)
            creature["curiosity"] = min(1.0, float(creature["curiosity"]) + 0.012)

        commitment = creature.get("behavior_commitment") or {}
        if int(commitment.get("ticks_remaining", 0)) > 0:
            event_type, summary, details, state = self._continue_committed_action(state)
            if state["creature"]["zone"] == "sleeping_nook" and state["creature"]["activity"] == "sleep":
                aftermath["sleep_nook_ticks"] = int(aftermath["sleep_nook_ticks"]) + 1
            habitat["shelf_count"] = sum(1 for o in state["objects"] if o["zone"] == "collection_shelf" and o["state"] == "placed")
            details["energy_after"] = round(float(state["creature"]["energy"]), 6)
            return event_type, summary, details, state

        zone = creature["zone"]
        recent = list(creature.get("recent_actions", []))
        nearby = self._object_in_zone(state, zone)
        carrying = creature.get("carrying")
        lighting = habitat["lighting"]
        intent = dict(context.get("intent") or {})
        intent_kind = str(intent.get("kind") or "")
        intent_stage = str(intent.get("stage") or "")
        intent_object_id = intent.get("object_id")

        weights: dict[str, float] = {}

        def add(action_name: str, weight: float) -> None:
            weights[action_name] = float(weights.get(action_name, 0.0)) + float(weight)

        if creature["activity"] == "sleep":
            wake_weight = 0.95 if creature["energy"] >= 0.86 or lighting in {"dawn", "day"} else 0.07
            add("wake", wake_weight)
            add("sleep", 1.35)
        elif carrying:
            # Carrying is itself an intention.  The pickup chooses one bounded
            # delivery destination; subsequent choices finish that small chain.
            add("idle", 0.08)
            add("rest", 0.06)
            delivery_target = str(intent.get("target_zone") or "")
            if delivery_target == zone:
                add("place", 3.30)
                add("walk", 0.10)
            else:
                add("walk", 2.55)
        else:
            if float(creature["energy"]) < 0.26 or (lighting == "night" and float(creature["energy"]) < 0.58):
                add("sleep", 1.65)
            add("idle", 0.58)
            add("rest", 0.72 + (1.0 - float(creature["energy"])) * 0.52)
            add("walk", 0.38)
            add("explore", 0.30 + float(creature["curiosity"]) * 0.18)
            if zone == "window":
                add("look_outside", 0.95 + (0.28 if habitat["weather"] != "clear" else 0.0))
            if nearby:
                add("inspect", 0.70 + float(creature["curiosity"]) * 0.22)
                add("carry", 0.24 + float(creature["curiosity"]) * 0.12)

        # A tiny routine context shapes only the next few choices.  It is not a
        # scheduler: weighted autonomy remains, but plausible continuations get
        # much more weight than unrelated room-crossing.
        movement_context_penalty = 1.0
        if intent_kind == "arrival_settle" and intent.get("zone") == zone:
            add("idle", 1.45)
            add("rest", 1.20)
            if zone == "activity_corner" and nearby:
                add("inspect", 0.75)
            movement_context_penalty = 0.08
        elif intent_kind == "window_session" and zone == "window":
            if intent_stage == "arrived":
                add("look_outside", 3.20)
                movement_context_penalty = 0.035
            else:
                add("look_outside", 0.85)
                add("idle", 1.15)
                add("rest", 0.85)
                movement_context_penalty = 0.12
        elif intent_kind == "object_session" and intent_stage == "inspected" and not carrying:
            preferred = next((o for o in nearby if o["id"] == intent_object_id and o["state"] == "placed"), None)
            if preferred is not None:
                add("carry", 3.60)
                add("inspect", 0.15)
                movement_context_penalty = 0.045
        elif intent_kind == "post_place":
            add("idle", 2.10)
            add("rest", 1.55)
            movement_context_penalty = 0.035
        elif intent_kind == "wake_recovery":
            add("idle", 2.25)
            add("rest", 1.75)
            movement_context_penalty = 0.025

        adjusted: list[tuple[str, float]] = []
        movement_recent = sum(1 for a in recent[-3:] if a in {"walk", "explore"})
        manipulation_recent = sum(1 for a in recent[-4:] if a in {"carry", "place"})
        for action_name, weight in weights.items():
            repeats = sum(1 for a in recent[-4:] if a == action_name)
            penalty = 1.0 if action_name == "sleep" else 0.52 ** repeats
            if action_name in {"walk", "explore"}:
                penalty *= 0.30 ** movement_recent
                penalty *= movement_context_penalty
            if action_name in {"carry", "place"}:
                penalty *= 0.52 ** manipulation_recent
            adjusted.append((action_name, max(0.008, weight * penalty)))
        action = self._weighted_pick(rng, adjusted)

        details: dict[str, Any] = {
            "from_zone": zone, "lighting": lighting, "weather": habitat["weather"],
            "decision": True, "intent_action": action,
        }
        event_type = "creature_activity"
        summary = "Moss is quietly awake."
        focus_object_id = None

        if action in {"walk", "explore"}:
            target = self._choose_destination(rng, state, context, zone=zone, carrying=carrying)
            destination = zone_anchor(target)
            self._route_creature(creature, details, destination=destination, destination_zone=target)
            creature["activity"] = "walk"
            creature["expression"] = "curious" if action == "explore" else "neutral"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - (0.045 if action == "explore" else 0.018))
            habitat["path_wear"][target] = int(habitat["path_wear"].get(target, 0)) + 1
            if habitat["path_wear"][target] in {6, 14}:
                mark = f"worn_{target}_{habitat['path_wear'][target]}"
                if mark not in habitat["marks"]:
                    habitat["marks"].append(mark)
            self._remember_zone(context, target)
            if carrying:
                carried = next(o for o in state["objects"] if o["id"] == carrying)
                carried["zone"] = target
                carried["x"] = creature["x"] + (-14 if creature["facing"] == "left" else 14)
                carried["y"] = creature["y"] - 22
                prior_intent = dict(context.get("intent") or {})
                context["intent"] = {
                    "kind": "object_session",
                    "stage": "arrived_with_object",
                    "object_id": carrying,
                    "target_zone": target,
                }
                if prior_intent.get("target_zone") and prior_intent.get("target_zone") != target:
                    details["intent_target_mismatch"] = True
                travel_purpose = "object_delivery"
            elif target == "window":
                context["intent"] = {"kind": "window_session", "stage": "arrived", "zone": target}
                travel_purpose = "window_session"
            else:
                context["intent"] = {"kind": "arrival_settle", "stage": "arrived", "zone": target}
                travel_purpose = "activity_session" if target == "activity_corner" else "settle_at_familiar_spot"
            details.update({"to_zone": target, "travel_purpose": travel_purpose})
            event_type = "creature_moved"
            summary = f"Moss headed from {zone.replace('_', ' ')} to {target.replace('_', ' ')} and settled in."
        elif action == "inspect" and nearby:
            obj = self._choose_object(rng, nearby, context, preferred_id=str(intent_object_id) if intent_object_id else None)
            target_x, target_y = int(obj["x"]), int(obj["y"])
            approach = interaction_approach(zone=zone, target_x=target_x, target_y=target_y, current_x=int(creature["x"]), current_y=int(creature["y"]))
            self._route_creature(creature, details, destination=approach, destination_zone=zone)
            contact = interaction_contact(zone=zone, target_x=target_x, target_y=target_y, approach=approach)
            details["contact_x"], details["contact_y"] = contact
            creature["facing"] = "right" if contact[0] >= int(creature["x"]) else "left"
            obj["times_inspected"] = int(obj["times_inspected"]) + 1
            creature["activity"] = "inspect"
            creature["expression"] = "curious"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.09)
            details.update({"object_id": obj["id"], "target_x": target_x, "target_y": target_y})
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            context["intent"] = {"kind": "object_session", "stage": "inspected", "object_id": obj["id"]}
            event_type = "object_inspected"
            summary = f"Moss stopped to inspect the {obj['name'].lower()}."
        elif action == "carry" and nearby:
            obj = self._choose_object(rng, nearby, context, preferred_id=str(intent_object_id) if intent_object_id else None)
            target_x, target_y = int(obj["x"]), int(obj["y"])
            approach = interaction_approach(zone=zone, target_x=target_x, target_y=target_y, current_x=int(creature["x"]), current_y=int(creature["y"]))
            self._route_creature(creature, details, destination=approach, destination_zone=zone)
            contact = interaction_contact(zone=zone, target_x=target_x, target_y=target_y, approach=approach)
            details["contact_x"], details["contact_y"] = contact
            creature["facing"] = "right" if contact[0] >= int(creature["x"]) else "left"
            creature["carrying"] = obj["id"]
            creature["activity"] = "carry"
            creature["expression"] = "excited"
            obj["state"] = "carried"
            obj["carried_by"] = creature["id"]
            obj["x"] = int(creature["x"]) + (-22 if creature["facing"] == "left" else 22)
            obj["y"] = int(creature["y"]) - 4
            details.update({"object_id": obj["id"], "target_x": target_x, "target_y": target_y})
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            if zone == "collection_shelf":
                delivery_target = self._weighted_pick(
                    rng,
                    [("open_space", 1.45), ("activity_corner", 1.20), ("window", 0.72)],
                )
            else:
                delivery_target = "collection_shelf"
            context["intent"] = {
                "kind": "object_session",
                "stage": "carrying",
                "object_id": obj["id"],
                "target_zone": delivery_target,
            }
            details["delivery_target_zone"] = delivery_target
            event_type = "object_picked_up"
            summary = f"Moss picked up the {obj['name'].lower()}."
        elif action == "place" and carrying:
            obj = next(o for o in state["objects"] if o["id"] == carrying)
            target_x, target_y = self._placement_position(state, obj, zone)
            approach = interaction_approach(zone=zone, target_x=target_x, target_y=target_y, current_x=int(creature["x"]), current_y=int(creature["y"]))
            self._route_creature(creature, details, destination=approach, destination_zone=zone)
            contact = interaction_contact(zone=zone, target_x=target_x, target_y=target_y, approach=approach)
            details["contact_x"], details["contact_y"] = contact
            creature["facing"] = "right" if contact[0] >= int(creature["x"]) else "left"
            obj["state"] = "placed"
            obj["carried_by"] = None
            obj["zone"] = zone
            obj["x"], obj["y"] = target_x, target_y
            obj["times_moved"] = int(obj["times_moved"]) + 1
            creature["carrying"] = None
            creature["activity"] = "place"
            creature["expression"] = "content"
            details.update({"object_id": obj["id"], "to_zone": zone, "x": obj["x"], "y": obj["y"], "target_x": target_x, "target_y": target_y})
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            context["intent"] = {"kind": "post_place", "stage": "settle", "object_id": obj["id"], "zone": zone}
            event_type = "object_placed"
            summary = f"Moss placed the {obj['name'].lower()} in the {zone.replace('_', ' ')} and regarded it for a moment."
        elif action == "sleep":
            support = (int(SLEEP_SUPPORT_ANCHOR["x"]), int(SLEEP_SUPPORT_ANCHOR["y"]))
            self._route_creature(creature, details, destination=support, destination_zone="sleeping_nook")
            details.update({"to_zone": "sleeping_nook", "supported_action": "sleep"})
            creature["activity"] = "sleep"
            creature["expression"] = "sleepy"
            aftermath["sleep_nook_ticks"] = int(aftermath["sleep_nook_ticks"]) + 1
            if before["creature"]["activity"] != "sleep":
                aftermath["sleep_nook_bouts"] = int(aftermath["sleep_nook_bouts"]) + 1
            context["intent"] = {"kind": "sleep_cycle", "stage": "sleeping", "zone": "sleeping_nook"}
            self._remember_zone(context, "sleeping_nook")
            event_type = "creature_slept"
            summary = "Moss entered the sleeping nook and curled up on the supported bed spot."
        elif action == "wake":
            creature["activity"] = "wake"
            creature["expression"] = "content"
            context["intent"] = {"kind": "wake_recovery", "stage": "woke", "zone": "sleeping_nook"}
            event_type = "creature_woke"
            summary = "Moss woke up, unfolded, and stayed near the bed before moving on."
        elif action == "rest":
            creature["activity"] = "rest"
            creature["expression"] = "content"
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.034)
            if intent_kind in {"arrival_settle", "post_place", "wake_recovery"}:
                context["intent"] = None
            elif intent_kind == "window_session" and intent_stage != "arrived":
                context["intent"] = None
            event_type = "creature_rested"
            summary = f"Moss rested for a while in the {zone.replace('_', ' ')}."
        elif action == "look_outside":
            destination = zone_anchor("window")
            self._route_creature(creature, details, destination=destination, destination_zone="window")
            details["supported_action"] = "window_watch"
            creature["activity"] = "look_outside"
            creature["expression"] = "content" if habitat["weather"] == "rain" else "curious"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.055)
            aftermath["window_watches"] = int(aftermath["window_watches"]) + 1
            if habitat["weather"] in {"rain", "mist"}:
                aftermath["wet_window_watches"] = int(aftermath["wet_window_watches"]) + 1
            context["intent"] = {"kind": "window_session", "stage": "watched", "zone": "window"}
            event_type = "window_watched"
            summary = f"Moss watched the {habitat['weather']} outside the window."
        else:
            creature["activity"] = "idle"
            creature["expression"] = "neutral"
            if intent_kind in {"arrival_settle", "post_place", "wake_recovery"}:
                context["intent"] = None
            elif intent_kind == "window_session" and intent_stage != "arrived":
                context["intent"] = None
            event_type = "creature_idled"
            summary = f"Moss lingered in the {zone.replace('_', ' ')}."

        if zone == "activity_corner" and action in {"idle", "rest", "inspect", "carry", "place"}:
            aftermath["activity_corner_uses"] = int(aftermath["activity_corner_uses"]) + 1
        creature["recent_actions"] = (recent + [action])[-8:]
        creature["focus_object_id"] = focus_object_id
        creature["behavior_commitment"] = {
            "action": action,
            "ticks_remaining": int(self.COMMITMENT_TICKS.get(action, 1)),
            "object_id": focus_object_id,
        }
        details["commitment_ticks_remaining"] = creature["behavior_commitment"]["ticks_remaining"]
        current_intent = context.get("intent") or {}
        details["routine_intent"] = current_intent.get("kind")
        details["routine_stage"] = current_intent.get("stage")
        habitat["shelf_count"] = sum(1 for o in state["objects"] if o["zone"] == "collection_shelf" and o["state"] == "placed")
        details["action"] = action
        details["energy_after"] = round(float(creature["energy"]), 6)
        return event_type, summary, details, state


class WorldEngine:
    def __init__(self, store: WorldStore, *, seed: int = 1701, minutes_per_tick: int = 1, snapshot_every: int = 20):
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
