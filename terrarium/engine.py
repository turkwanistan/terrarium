from __future__ import annotations

import hashlib
import random
import threading
import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .events import make_event, state_patch
from .consequences import (
    CONSEQUENCE_MEMORY_SCHEMA, consequence_opportunities, ensure_consequence_memory, find_consequence,
    mark_consequence_revisited, prune_consequence_memory, record_consequence,
)
from .models import (
    AFFORDANCE_HISTORY_SCHEMA, BEHAVIOR_CONTEXT_SCHEMA, HABIT_CONTEXTS, HABIT_PROFILE_SCHEMA, OBJECT_AFFORDANCE_SCHEMA,
    PLACEMENT_SLOTS, RNG_STREAM_VERSION, RULES_VERSION, ZONES, clone_state, lighting_for, normalize_object_identity,
    object_affordances, weather_for, normalize_seasonal_clock, utc_now,
)
from .spatial import (
    FAVORITE_SPOTS, SLEEP_SUPPORT_ANCHOR, SPATIAL_SCHEMA, interaction_approach, interaction_contact, point_is_walkable, route_between,
    route_length, route_payload, zone_anchor,
)
from .situations import (
    SITUATIONAL_EVENTS_SCHEMA, active_event, can_defer_event, choose_attention, event_target,
    mark_attention, mark_engaged, should_interrupt_event, update_situational_events,
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
        "carry": 1, "place": 2, "nudge": 2, "loaf": 4, "groom": 4, "stretch": 2,
        "react": 3, "look_outside": 5, "sleep": 6, "wake": 2,
    }

    """Pure deterministic world transition logic.

    The only entropy source is the PRNG state stored in canonical world state.
    """

    def __init__(self, *, minutes_per_tick: int = 1):
        self.minutes_per_tick = int(minutes_per_tick)

    def _rng(self, state: dict[str, Any]) -> random.Random:
        # Keep host compatibility with Python 3.10. Python 3.12 accepts
        # same-quote expressions inside f-strings (PEP 701); 3.10 does not.
        material = f"{state['seed']}:{RNG_STREAM_VERSION}:{int(state['tick']) + 1}".encode("utf-8")
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
    def _habit_profile(state: dict[str, Any]) -> dict[str, Any]:
        """Return the bounded long-horizon habit profile, migrating old worlds neutrally.

        Existing v3 worlds do not contain enough durable evidence to reconstruct
        exact historical preferences without replaying and reinterpreting their
        entire ledger under rules that did not yet exist.  Migration therefore
        preserves the world exactly and starts the new profile at a documented
        neutral baseline; all subsequent learning comes from canonical experience.
        """
        creature = state["creature"]
        object_ids = [str(obj["id"]) for obj in state["objects"]]
        profile = creature.get("habit_profile")
        if not isinstance(profile, dict) or profile.get("schema") != HABIT_PROFILE_SCHEMA:
            profile = {
                "schema": HABIT_PROFILE_SCHEMA,
                "migration_origin": "neutral-existing-world",
                "experience_count": 0,
                "zone_affinity": {name: 0.0 for name in ZONES},
                "object_affinity": {object_id: 0.0 for object_id in object_ids},
                "context_zone_affinity": {
                    context: {name: 0.0 for name in ZONES} for context in HABIT_CONTEXTS
                },
            }
            creature["habit_profile"] = profile

        def clean_map(raw: Any, keys: list[str]) -> dict[str, float]:
            raw = raw if isinstance(raw, dict) else {}
            return {
                key: round(max(0.0, min(1.0, float(raw.get(key, 0.0) or 0.0))), 6)
                for key in keys
            }

        profile["schema"] = HABIT_PROFILE_SCHEMA
        profile.setdefault("migration_origin", "native")
        profile["experience_count"] = max(0, int(profile.get("experience_count", 0)))
        profile["zone_affinity"] = clean_map(profile.get("zone_affinity"), list(ZONES))
        profile["object_affinity"] = clean_map(profile.get("object_affinity"), object_ids)
        context_raw = profile.get("context_zone_affinity")
        context_raw = context_raw if isinstance(context_raw, dict) else {}
        profile["context_zone_affinity"] = {
            context: clean_map(context_raw.get(context), list(ZONES)) for context in HABIT_CONTEXTS
        }
        return profile

    @staticmethod
    def _affordance_history(state: dict[str, Any]) -> dict[str, Any]:
        """Additively migrate bounded repertoire aftermath without inventing past activity."""
        habitat = state["habitat"]
        history = habitat.get("affordance_history")
        if not isinstance(history, dict) or history.get("schema") != AFFORDANCE_HISTORY_SCHEMA:
            history = {
                "schema": AFFORDANCE_HISTORY_SCHEMA,
                "completed_families": {},
                "object_nudges": {},
                "zone_comfort": {name: 0 for name in ZONES},
                "zone_arrangements": {name: 0 for name in ZONES},
                "last_weather_reaction_block": -1,
            }
            habitat["affordance_history"] = history
        history["schema"] = AFFORDANCE_HISTORY_SCHEMA
        history["completed_families"] = {str(k): max(0, int(v)) for k, v in dict(history.get("completed_families") or {}).items()}
        history["object_nudges"] = {str(k): max(0, int(v)) for k, v in dict(history.get("object_nudges") or {}).items()}
        history["zone_comfort"] = {name: max(0, int((history.get("zone_comfort") or {}).get(name, 0))) for name in ZONES}
        history["zone_arrangements"] = {name: max(0, int((history.get("zone_arrangements") or {}).get(name, 0))) for name in ZONES}
        history["last_weather_reaction_block"] = int(history.get("last_weather_reaction_block", -1))
        for obj in state["objects"]:
            obj["times_nudged"] = max(0, int(obj.get("times_nudged", 0)))
        return history

    @staticmethod
    def _set_object_interaction_state(obj: dict[str, Any], new_state: str) -> bool:
        normalize_object_identity(obj)
        new_state = str(new_state)
        if str(obj.get("interaction_state")) == new_state:
            return False
        obj["interaction_state"] = new_state
        obj["state_transitions"] = int(obj.get("state_transitions", 0)) + 1
        return True

    @staticmethod
    def _activity_family(action: str) -> str:
        return {
            "idle": "idle", "rest": "comfort", "loaf": "comfort", "stretch": "comfort",
            "groom": "self_care", "walk": "travel", "explore": "travel",
            "inspect": "investigate", "carry": "arrange", "place": "arrange",
            "nudge": "play", "look_outside": "observe", "react": "react",
            "sleep": "sleep", "wake": "sleep",
        }.get(action, action)

    def _record_affordance(self, state: dict[str, Any], *, action: str, zone: str, object_id: str | None) -> str:
        history = self._affordance_history(state)
        family = self._activity_family(action)
        families = history["completed_families"]
        families[family] = int(families.get(family, 0)) + 1
        if action in {"rest", "loaf", "groom", "stretch"} and zone in ZONES:
            history["zone_comfort"][zone] = int(history["zone_comfort"][zone]) + 1
        if action == "place" and zone in ZONES:
            history["zone_arrangements"][zone] = int(history["zone_arrangements"][zone]) + 1
        if action == "nudge" and object_id:
            nudges = history["object_nudges"]
            nudges[object_id] = int(nudges.get(object_id, 0)) + 1
        return family

    @staticmethod
    def _relative_affinity(values: dict[str, float], key: str, *, strength: float) -> float:
        """Convert bounded memory into a normalized multiplier with an exploration floor."""
        if not values or key not in values:
            return 1.0
        mean = sum(float(value) for value in values.values()) / len(values)
        relative = float(values.get(key, 0.0)) - mean
        return max(0.68, min(1.72, 1.0 + strength * relative))

    @staticmethod
    def _habit_maturity(profile: dict[str, Any] | None) -> float:
        if not profile:
            return 0.0
        experiences = max(0, int(profile.get("experience_count", 0)))
        return max(0.0, min(1.0, (experiences - 180) / 720.0))

    @staticmethod
    def _reinforce_map(values: dict[str, float], key: str, amount: float) -> None:
        # Slow global forgetting prevents permanent lock-in; saturating reward
        # prevents runaway reinforcement.  Rounded storage keeps exact replay
        # stable across serialization/restart boundaries.
        for name in list(values):
            values[name] = round(max(0.0, min(1.0, float(values[name]) * 0.9985)), 6)
        current = float(values.get(key, 0.0))
        values[key] = round(max(0.0, min(1.0, current + amount * (1.0 - current))), 6)

    def _learn_from_decision(
        self,
        state: dict[str, Any],
        *,
        action: str,
        zone: str,
        object_id: str | None,
        lighting: str,
    ) -> None:
        profile = self._habit_profile(state)
        zone_reward = {
            "idle": 0.010, "rest": 0.014, "loaf": 0.018, "groom": 0.010, "stretch": 0.010,
            "look_outside": 0.020, "react": 0.008, "inspect": 0.012, "nudge": 0.014,
            "carry": 0.008, "place": 0.016, "sleep": 0.014,
        }.get(action, 0.0)
        object_reward = {"inspect": 0.018, "nudge": 0.020, "carry": 0.012, "place": 0.020}.get(action, 0.0)
        if zone_reward > 0.0 and zone in ZONES:
            self._reinforce_map(profile["zone_affinity"], zone, zone_reward)
            context = lighting if lighting in HABIT_CONTEXTS else "day"
            context_reward = zone_reward * (1.20 if action in {"rest", "loaf", "look_outside", "sleep"} else 0.85)
            self._reinforce_map(profile["context_zone_affinity"][context], zone, context_reward)
            profile["experience_count"] = int(profile["experience_count"]) + 1
        if object_reward > 0.0 and object_id and object_id in profile["object_affinity"]:
            self._reinforce_map(profile["object_affinity"], object_id, object_reward)

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
        habit_profile: dict[str, Any] | None = None,
        preferred_id: str | None = None,
        required_affordance: str | None = None,
    ) -> dict[str, Any]:
        candidates = [
            o for o in nearby
            if o["state"] == "placed" and (required_affordance is None or required_affordance in object_affordances(o))
        ]
        if not candidates:
            raise ValueError(f"no nearby object supports affordance {required_affordance!r}")
        if preferred_id:
            preferred = next((o for o in candidates if o["id"] == preferred_id), None)
            if preferred is not None:
                return preferred
        recent = list(context.get("recent_objects", []))
        weighted: list[tuple[str, float]] = []
        by_id = {str(o["id"]): o for o in candidates}
        last_object_id = recent[-1] if recent else None
        alternatives_exist = bool(last_object_id) and any(str(o["id"]) != last_object_id for o in candidates)
        for obj in candidates:
            object_id = str(obj["id"])
            # A completed object session gets a short, deterministic "done with
            # this for now" inhibition whenever another local object exists.
            if alternatives_exist and object_id == last_object_id:
                continue
            weight = 1.0 / (1.0 + 0.025 * min(20, int(obj.get("times_inspected", 0))))
            if object_id in recent[-4:]:
                weight *= 0.42
            if habit_profile is not None:
                weight *= self._relative_affinity(
                    habit_profile.get("object_affinity", {}), object_id, strength=1.80 * self._habit_maturity(habit_profile)
                )
            weighted.append((object_id, max(0.035, weight)))
        return by_id[self._weighted_pick(rng, weighted)]

    def _choose_destination(
        self,
        rng: random.Random,
        state: dict[str, Any],
        context: dict[str, Any],
        *,
        zone: str,
        carrying: str | None,
        habit_profile: dict[str, Any] | None = None,
    ) -> str:
        """Choose travel as a consequence of context instead of a uniform room hop."""
        intent = dict(context.get("intent") or {})
        target_zone = str(intent.get("target_zone") or "")
        if target_zone in ZONES and target_zone != zone and (carrying or str(intent.get("kind") or "") == "weather_reaction"):
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
                weight *= 0.07
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
                if habit_profile is not None:
                    weight *= self._relative_affinity(
                        habit_profile.get("zone_affinity", {}), target, strength=1.32 * self._habit_maturity(habit_profile)
                    )
                    contextual = (habit_profile.get("context_zone_affinity", {}) or {}).get(
                        str(state["habitat"]["lighting"]), {}
                    )
                    weight *= self._relative_affinity(contextual, target, strength=1.00 * self._habit_maturity(habit_profile))
            weighted.append((target, max(0.045, weight)))
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

    @staticmethod
    def _nudge_position(state: dict[str, Any], obj: dict[str, Any]) -> tuple[int, int]:
        zone = str(obj["zone"])
        slots = PLACEMENT_SLOTS[zone]
        material = f"nudge:{obj['id']}:{zone}:{int(obj.get('times_nudged', 0)) + 1}".encode("utf-8")
        start = int.from_bytes(hashlib.sha256(material).digest()[:2], "big") % len(slots)
        occupied = [
            (int(other["x"]), int(other["y"]))
            for other in state["objects"]
            if other["id"] != obj["id"] and other["state"] == "placed" and other["zone"] == zone
        ]
        old = (int(obj["x"]), int(obj["y"]))
        for offset in range(len(slots)):
            candidate = slots[(start + offset) % len(slots)]
            if candidate == old:
                continue
            if all((candidate[0] - ox) ** 2 + (candidate[1] - oy) ** 2 >= 20 ** 2 for ox, oy in occupied):
                return candidate
        return old

    def _choose_arrangement_destination(
        self, rng: random.Random, state: dict[str, Any], *, zone: str, object_id: str, habit_profile: dict[str, Any]
    ) -> str:
        profile_maturity = self._habit_maturity(habit_profile)
        obj = next((item for item in state["objects"] if str(item["id"]) == str(object_id)), None)
        archetype = str((obj or {}).get("archetype") or "keepsake")
        object_values = habit_profile.get("object_affinity", {})
        object_mean = sum(float(v) for v in object_values.values()) / max(1, len(object_values))
        object_bias = max(-0.25, min(0.35, float(object_values.get(object_id, 0.0)) - object_mean)) * profile_maturity
        if zone == "collection_shelf":
            base = {"open_space": 1.35, "activity_corner": 1.20, "window": 0.82, "sleeping_nook": 0.78}
        else:
            # The shelf remains a useful collection destination, but mature
            # habits can now plausibly turn preferred zones into personal spaces.
            base = {"collection_shelf": 1.40, "open_space": 1.08, "activity_corner": 1.10, "window": 0.82, "sleeping_nook": 0.84}
        weighted: list[tuple[str, float]] = []
        context_values = (habit_profile.get("context_zone_affinity", {}) or {}).get(str(state["habitat"]["lighting"]), {})
        for target, weight in base.items():
            if target == zone:
                continue
            # Object identity shapes plausible arrangements before learned habit
            # nudges them further. This remains a tendency, not a hard destination.
            if archetype == "rolling":
                weight *= {"open_space": 1.50, "activity_corner": 1.08, "collection_shelf": 0.72, "window": 0.78, "sleeping_nook": 0.82}.get(target, 1.0)
            elif archetype == "soft_nesting":
                weight *= {"sleeping_nook": 1.75, "open_space": 1.45, "activity_corner": 0.82, "window": 0.68, "collection_shelf": 0.52}.get(target, 1.0)
            elif archetype == "delicate":
                weight *= {"window": 1.35, "collection_shelf": 1.05, "open_space": 0.90, "activity_corner": 0.86, "sleeping_nook": 0.84}.get(target, 1.0)
            elif archetype == "keepsake":
                weight *= {"collection_shelf": 1.55, "activity_corner": 1.05, "open_space": 0.90, "window": 0.84, "sleeping_nook": 0.82}.get(target, 1.0)
            habit = self._relative_affinity(habit_profile.get("zone_affinity", {}), target, strength=1.60 * profile_maturity)
            contextual = self._relative_affinity(context_values, target, strength=1.10 * profile_maturity)
            if target != "collection_shelf":
                weight *= 1.0 + max(0.0, object_bias) * 1.8
            elif object_bias > 0.0:
                weight *= max(0.70, 1.0 - object_bias)
            weighted.append((target, max(0.05, weight * habit * contextual)))
        return self._weighted_pick(rng, weighted)

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
        elif visible == "nudge":
            creature["activity"] = "nudge"
            creature["expression"] = "excited"
        elif visible == "loaf":
            creature["activity"] = "loaf"
            creature["expression"] = "content"
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.018)
        elif visible == "groom":
            creature["activity"] = "groom"
            creature["expression"] = "content"
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.012)
        elif visible == "stretch":
            creature["activity"] = "stretch"
            creature["expression"] = "content"
        elif visible == "react":
            creature["activity"] = "react"
            creature["expression"] = "curious"
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
            "activity_family": self._activity_family(intent),
            "affordance_schema": AFFORDANCE_HISTORY_SCHEMA,
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
            "nudge": "Moss stayed with the object after nudging it into a new position.",
            "loaf": "Moss stayed tucked into a comfortable loaf.",
            "groom": "Moss continued a slow grooming session.",
            "stretch": "Moss held a long, relaxed stretch before settling.",
            "react": "Moss stayed alert to the change outside for another moment.",
            "idle": "Moss paused, planted and quiet, before choosing what to do next.",
        }.get(visible, "Moss stayed with the current activity.")
        return "creature_activity", summary, details, state

    @staticmethod
    def _annotate_situation(
        details: dict[str, Any],
        state: dict[str, Any],
        transition: dict[str, Any],
        *,
        event: dict[str, Any] | None = None,
        role: str | None = None,
        preempted_action: str | None = None,
    ) -> None:
        active = event or active_event(state)
        if active is not None:
            details["world_event_id"] = str(active["id"])
            details["world_event_type"] = str(active["type"])
            details["world_event_attention_status"] = str(active.get("attention_status") or "pending")
        if role:
            details["world_event_role"] = role
        if preempted_action:
            details["interrupted_action"] = preempted_action
        if transition.get("started"):
            started = transition["started"]
            details["world_event_started"] = {
                "id": str(started["id"]), "type": str(started["type"]),
                "start_world_minute": int(started["start_world_minute"]),
                "end_world_minute": int(started["end_world_minute"]),
            }
        if transition.get("ended"):
            details["world_event_ended"] = dict(transition["ended"])
        details["situational_events_schema"] = SITUATIONAL_EVENTS_SCHEMA

    @staticmethod
    def _annotate_consequence(
        details: dict[str, Any],
        state: dict[str, Any],
        *,
        role: str | None = None,
        memory_id: str | None = None,
    ) -> None:
        memory = ensure_consequence_memory(state)
        context = ((state.get("creature") or {}).get("behavior_context") or {})
        intent = context.get("intent") if isinstance(context, dict) else None
        intent = intent if isinstance(intent, dict) else {}
        selected_id = memory_id or intent.get("memory_id")
        entry = find_consequence(state, str(selected_id)) if selected_id else None
        details["consequence_memory_schema"] = CONSEQUENCE_MEMORY_SCHEMA
        details["consequence_memory_open"] = len(memory.get("entries") or [])
        details["consequence_revisit_count"] = int(memory.get("revisit_count", 0))
        if entry is not None:
            details["consequence_memory_id"] = str(entry["id"])
            details["consequence_kind"] = str(entry.get("kind") or "aftermath")
            details["consequence_created_world_minute"] = int(entry.get("created_world_minute", state.get("world_minutes", 0)))
            details["consequence_eligible_after_world_minute"] = int(entry.get("created_world_minute", state.get("world_minutes", 0))) + int(entry.get("delay_minutes", 45))
            details["consequence_source"] = dict(entry.get("source") or {})
        if role:
            details["consequence_role"] = str(role)

    def step(self, state: dict[str, Any], *, observed_at_utc: str | None = None) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
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
        habit_profile = self._habit_profile(state)
        self._affordance_history(state)
        ensure_consequence_memory(state)
        prune_consequence_memory(state)
        for obj in state["objects"]:
            normalize_object_identity(obj)
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
                "loaf_sessions": 0, "groom_sessions": 0, "stretch_sessions": 0,
                "object_nudges": 0, "arrangement_places": 0, "weather_reactions": 0,
            },
        )
        for key in ("sleep_nook_ticks", "sleep_nook_bouts", "window_watches", "wet_window_watches", "activity_corner_uses", "loaf_sessions", "groom_sessions", "stretch_sessions", "object_nudges", "arrangement_places", "weather_reactions"):
            aftermath.setdefault(key, 0)
        state["tick"] = int(state["tick"]) + 1
        state["world_minutes"] = int(state["world_minutes"]) + self.minutes_per_tick
        habitat["lighting"] = lighting_for(int(state["world_minutes"]))
        habitat["weather"] = weather_for(int(state["world_minutes"]), int(state["seed"]))
        season_before = ((before.get("habitat") or {}).get("seasonal_clock") or {})
        season_now = normalize_seasonal_clock(state, observed_at_utc=observed_at_utc)
        event_transition = update_situational_events(state)
        current_world_event = active_event(state)
        ended_world_event = event_transition.get("ended")
        if ended_world_event and str(ended_world_event.get("outcome")) in {"engaged", "oriented"}:
            record_consequence(
                state,
                kind="situational_aftermath",
                zone=str(ended_world_event.get("source_zone") or "window"),
                strength=0.72 if ended_world_event.get("outcome") == "engaged" else 0.48,
                source={
                    "cause": "situational_event",
                    "world_event_id": ended_world_event.get("id"),
                    "world_event_type": ended_world_event.get("type"),
                    "world_event_outcome": ended_world_event.get("outcome"),
                },
                min_delay_minutes=90,
            )

        # Drives change every heartbeat even when a behavioral intent is held.
        if creature["activity"] == "sleep":
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.075)
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.02)
        else:
            creature["energy"] = max(0.0, float(creature["energy"]) - 0.018)
            creature["curiosity"] = min(1.0, float(creature["curiosity"]) + 0.012)

        commitment = creature.get("behavior_commitment") or {}
        preempted_action: str | None = None
        if current_world_event is not None and event_transition.get("started") and int(commitment.get("ticks_remaining", 0)) > 0:
            if should_interrupt_event(state, current_world_event, commitment):
                preempted_action = str(commitment.get("action") or "")
                mark_attention(current_world_event, "interrupt", int(state["world_minutes"]), interrupted_action=preempted_action)
                habitat["situational_events"]["outcome_counts"]["interrupted"] += 1
                commitment["ticks_remaining"] = 0
                creature["behavior_commitment"] = commitment
            elif can_defer_event(state, current_world_event, commitment):
                mark_attention(current_world_event, "defer", int(state["world_minutes"]))
                habitat["situational_events"]["outcome_counts"]["deferred"] += 1

        if int((creature.get("behavior_commitment") or {}).get("ticks_remaining", 0)) > 0:
            event_type, summary, details, state = self._continue_committed_action(state)
            if state["creature"]["zone"] == "sleeping_nook" and state["creature"]["activity"] == "sleep":
                aftermath["sleep_nook_ticks"] = int(aftermath["sleep_nook_ticks"]) + 1
            habitat["shelf_count"] = sum(1 for o in state["objects"] if o["zone"] == "collection_shelf" and o["state"] == "placed")
            details["energy_after"] = round(float(state["creature"]["energy"]), 6)
            details["season"] = season_now["season"]
            details["season_stage"] = season_now["stage"]
            if season_before.get("season") != season_now["season"] or season_before.get("stage") != season_now["stage"]:
                details["season_transition"] = {"from_season": season_before.get("season"), "from_stage": season_before.get("stage"), "to_season": season_now["season"], "to_stage": season_now["stage"]}
            self._annotate_situation(details, state, event_transition, event=current_world_event, role="deferred_during_commitment" if current_world_event and current_world_event.get("attention_status") == "deferred" else None)
            self._annotate_consequence(details, state)
            return event_type, summary, details, state

        zone = creature["zone"]
        recent = list(creature.get("recent_actions", []))
        nearby = self._object_in_zone(state, zone)
        inspectable = [o for o in nearby if "inspect" in object_affordances(o)]
        carryable = [o for o in nearby if "carry" in object_affordances(o)]
        nudgeable = [o for o in nearby if "nudge" in object_affordances(o)]
        carrying = creature.get("carrying")
        lighting = habitat["lighting"]
        intent = dict(context.get("intent") or {})
        intent_kind = str(intent.get("kind") or "")
        intent_stage = str(intent.get("stage") or "")
        intent_object_id = intent.get("object_id")
        forced_action: str | None = None
        world_event_role: str | None = None
        consequence_role: str | None = None
        linked_consequence_id: str | None = str(intent.get("memory_id")) if intent.get("memory_id") else None
        linked_event = current_world_event
        linked_target: dict[str, Any] | None = None

        if intent_kind == "consequence_revisit":
            entry = find_consequence(state, str(linked_consequence_id or ""))
            if entry is None or bool(entry.get("resolved")) or int(state["world_minutes"]) > int(entry.get("expires_world_minute", state["world_minutes"])):
                context["intent"] = None
                intent = {}; intent_kind = ""; intent_stage = ""; intent_object_id = None; linked_consequence_id = None
            else:
                target_zone = str(intent.get("target_zone") or entry.get("zone"))
                target_object_id = intent.get("object_id")
                engage_action = str(intent.get("engage_action") or ("inspect" if target_object_id else ("look_outside" if target_zone == "window" else "loaf")))
                target_x, target_y = zone_anchor(target_zone)
                if target_object_id:
                    target_obj = next((o for o in state["objects"] if str(o["id"]) == str(target_object_id) and o.get("state") == "placed"), None)
                    if target_obj is not None:
                        target_x, target_y = int(target_obj["x"]), int(target_obj["y"])
                distance = ((int(creature["x"]) - int(target_x)) ** 2 + (int(creature["y"]) - int(target_y)) ** 2) ** 0.5
                if intent_stage == "noticed":
                    if str(creature["zone"]) != target_zone or distance > 28:
                        forced_action = "walk"; consequence_role = "approach"
                    else:
                        forced_action = engage_action; consequence_role = "engage"
                elif intent_stage == "arrived":
                    forced_action = engage_action; consequence_role = "engage"

        ended = event_transition.get("ended")
        if ended and intent_kind == "situational_event" and str(intent.get("event_id") or "") == str(ended.get("id") or ""):
            context["intent"] = {"kind": "event_recovery", "stage": "settle", "event_type": ended.get("type")}
            intent = dict(context["intent"]); intent_kind = "event_recovery"; intent_stage = "settle"

        if linked_event is not None:
            linked_target = event_target(linked_event, int(state["world_minutes"]))
            event_id = str(linked_event["id"])
            if intent_kind == "situational_event" and str(intent.get("event_id") or "") == event_id:
                if intent_stage in {"noticed", "deferred"}:
                    distance = ((int(creature["x"]) - int(linked_target["x"])) ** 2 + (int(creature["y"]) - int(linked_target["y"])) ** 2) ** 0.5
                    if str(creature["zone"]) != str(linked_target["zone"]) or distance > 18:
                        forced_action = "walk"; world_event_role = "approach"
                    else:
                        forced_action = str(linked_target["engage_action"]); world_event_role = "engage"
                elif intent_stage == "arrived":
                    forced_action = str(linked_target["engage_action"]); world_event_role = "engage"
                elif intent_stage == "engaged":
                    distance = ((int(creature["x"]) - int(linked_target["x"])) ** 2 + (int(creature["y"]) - int(linked_target["y"])) ** 2) ** 0.5
                    if linked_event.get("type") == "sunlight" and distance > 18 and int(linked_event.get("follow_moves", 0)) < 1:
                        forced_action = "walk"; world_event_role = "follow_affordance"
                    else:
                        context["intent"] = {"kind": "event_recovery", "stage": "settle", "event_type": linked_event.get("type")}
                        intent = dict(context["intent"]); intent_kind = "event_recovery"; intent_stage = "settle"
            elif str(linked_event.get("attention_status")) in {"deferred", "interrupted"}:
                context["intent"] = {
                    "kind": "situational_event", "stage": "noticed", "event_id": event_id,
                    "event_type": linked_event["type"], "target_zone": linked_target["zone"],
                }
                intent = dict(context["intent"]); intent_kind = "situational_event"; intent_stage = "noticed"
                forced_action = "react"
                world_event_role = "notice_after_interrupt" if linked_event.get("attention_status") == "interrupted" else "notice_after_defer"
            elif str(linked_event.get("attention_status")) == "pending":
                protected_object_chain = bool(carrying) or intent_kind == "object_session"
                if creature.get("activity") == "sleep" or protected_object_chain:
                    choice = "ignored"
                else:
                    choice = choose_attention(state, linked_event)
                mark_attention(linked_event, choice, int(state["world_minutes"]))
                if choice == "engage":
                    context["intent"] = {
                        "kind": "situational_event", "stage": "noticed", "event_id": event_id,
                        "event_type": linked_event["type"], "target_zone": linked_target["zone"],
                    }
                    intent = dict(context["intent"]); intent_kind = "situational_event"; intent_stage = "noticed"
                    forced_action = "react"; world_event_role = "notice"
                elif choice == "orient":
                    forced_action = "react"; world_event_role = "orient"

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
            add("idle", 0.52)
            add("rest", 0.64 + (1.0 - float(creature["energy"])) * 0.48)
            if zone != "collection_shelf":
                loaf_habit = self._relative_affinity(
                    habit_profile.get("zone_affinity", {}), zone, strength=1.35 * self._habit_maturity(habit_profile)
                )
                add("loaf", (0.20 + float(creature["comfort"]) * 0.06) * loaf_habit)
            add("groom", 0.14)
            add("stretch", 0.11)
            weather_block = int(state["world_minutes"]) // 180
            last_reaction_block = int((habitat.get("affordance_history") or {}).get("last_weather_reaction_block", -1))
            if habitat["weather"] in {"rain", "mist"} and zone != "window" and weather_block != last_reaction_block:
                add("react", 1.05)
            add("walk", 0.36)
            add("explore", 0.30 + float(creature["curiosity"]) * 0.18)
            if zone == "window":
                add("look_outside", 0.95 + (0.28 if habitat["weather"] != "clear" else 0.0))
            if inspectable:
                add("inspect", 0.70 + float(creature["curiosity"]) * 0.22)
            if carryable:
                add("carry", 0.24 + float(creature["curiosity"]) * 0.12)

        consequence_candidate: dict[str, Any] | None = None
        if not carrying and linked_event is None and not intent_kind and creature.get("activity") != "sleep":
            opportunities = consequence_opportunities(state)
            if opportunities:
                candidate = opportunities[0]
                gate_material = f"{candidate['memory_id']}:{int(state['tick'])}:revisit".encode("utf-8")
                gate = int.from_bytes(hashlib.sha256(gate_material).digest()[:2], "big") % 1000
                threshold = 6 + int(float(candidate["score"]) * 12.0)
                if gate < threshold:
                    consequence_candidate = candidate
                    linked_consequence_id = str(candidate["memory_id"])
                    context["intent"] = {
                        "kind": "consequence_revisit",
                        "stage": "noticed",
                        "memory_id": linked_consequence_id,
                        "target_zone": str(candidate["zone"]),
                        "object_id": candidate.get("object_id"),
                        "engage_action": str(candidate["engage_action"]),
                    }
                    intent = dict(context["intent"]); intent_kind = "consequence_revisit"; intent_stage = "noticed"
                    intent_object_id = intent.get("object_id")
                    consequence_role = "recognize"
                    forced_action = "react"

        # A tiny routine context shapes only the next few choices.  It is not a
        # scheduler: weighted autonomy remains, but plausible continuations get
        # much more weight than unrelated room-crossing.
        movement_context_penalty = 1.0
        if intent_kind == "arrival_settle" and intent.get("zone") == zone:
            add("idle", 1.25)
            add("rest", 1.10)
            if zone != "collection_shelf":
                loaf_habit = self._relative_affinity(
                    habit_profile.get("zone_affinity", {}), zone, strength=1.35 * self._habit_maturity(habit_profile)
                )
                add("loaf", 0.72 * loaf_habit)
            if zone == "activity_corner" and nearby:
                add("inspect", 0.75)
            movement_context_penalty = 0.08
        elif intent_kind == "window_session" and zone == "window":
            if intent_stage == "arrived":
                add("look_outside", 3.45)
                movement_context_penalty = 0.035
            else:
                add("look_outside", 0.85)
                add("idle", 1.15)
                add("rest", 0.85)
                movement_context_penalty = 0.12
        elif intent_kind == "object_session" and intent_stage == "inspected" and not carrying:
            preferred = next((o for o in nearby if o["id"] == intent_object_id and o["state"] == "placed"), None)
            if preferred is not None:
                affordances = set(object_affordances(preferred))
                if "carry" in affordances:
                    add("carry", 3.10)
                if "nudge" in affordances:
                    add("nudge", 1.75)
                if "nest" in affordances:
                    add("loaf", 2.80)
                add("inspect", 0.12)
                if "carry" not in affordances and "nudge" not in affordances and "nest" not in affordances:
                    add("idle", 1.20); add("rest", 0.85)
                movement_context_penalty = 0.045
        elif intent_kind == "object_session" and intent_stage == "rolled" and not carrying:
            preferred = next((o for o in nearby if o["id"] == intent_object_id and o["state"] == "placed"), None)
            if preferred is not None:
                add("inspect", 4.60)
                movement_context_penalty = 0.02
        elif intent_kind == "object_session" and intent_stage == "rumpled" and not carrying:
            preferred = next((o for o in nearby if o["id"] == intent_object_id and o["state"] == "placed"), None)
            if preferred is not None and "nest" in object_affordances(preferred):
                add("loaf", 5.20)
                add("inspect", 0.35)
                movement_context_penalty = 0.02
        elif intent_kind == "object_session" and intent_stage in {"recovered", "nested"} and not carrying:
            add("idle", 1.80)
            add("rest", 1.25)
            movement_context_penalty = 0.025
        elif intent_kind == "post_place":
            add("idle", 2.10)
            add("rest", 1.55)
            movement_context_penalty = 0.035
        elif intent_kind == "wake_recovery":
            add("idle", 2.25)
            add("rest", 1.75)
            add("stretch", 0.90)
            movement_context_penalty = 0.025
        elif intent_kind == "weather_reaction" and zone != "window":
            add("walk", 4.20)
            add("idle", 0.10)
            movement_context_penalty = 1.0
        elif intent_kind in {"event_recovery", "consequence_recovery"}:
            add("idle", 2.35)
            add("rest", 1.85)
            if zone != "collection_shelf":
                add("loaf", 0.55)
            movement_context_penalty = 0.03

        # Strongly preserve the causal middle of short activities. A nudge is
        # not complete until Moss regards the displaced object; noticing weather
        # is not a decorative reaction if Moss immediately forgets to go look.
        if intent_kind == "wake_recovery":
            for name in list(weights):
                if name not in {"idle", "rest", "stretch", "loaf"}:
                    weights[name] *= 0.035
            weights["idle"] = weights.get("idle", 0.0) + 2.20
            weights["rest"] = weights.get("rest", 0.0) + 1.75
            weights["stretch"] = weights.get("stretch", 0.0) + 1.35
        elif intent_kind == "window_session" and intent_stage == "arrived" and zone == "window":
            for name in list(weights):
                if name != "look_outside":
                    weights[name] *= 0.06
            weights["look_outside"] = weights.get("look_outside", 0.0) + 5.20
        elif intent_kind == "object_session" and intent_stage == "inspected" and not carrying:
            preferred = next((o for o in nearby if o["id"] == intent_object_id and o["state"] == "placed"), None)
            if preferred is not None:
                affordances = set(object_affordances(preferred))
                allowed = {"inspect"}
                if "carry" in affordances:
                    allowed.add("carry")
                if "nudge" in affordances:
                    allowed.add("nudge")
                if "nest" in affordances:
                    allowed.add("loaf")
                for name in list(weights):
                    if name not in allowed and name != "sleep":
                        weights[name] *= 0.06
                if "carry" in allowed:
                    weights["carry"] = weights.get("carry", 0.0) + 3.20
                if "nudge" in allowed:
                    weights["nudge"] = weights.get("nudge", 0.0) + 2.20
                if "loaf" in allowed:
                    weights["loaf"] = weights.get("loaf", 0.0) + 3.00
                weights["inspect"] = weights.get("inspect", 0.0) * 0.22
                weights["sleep"] = weights.get("sleep", 0.0) * 0.20
        elif intent_kind == "object_session" and intent_stage == "rolled" and not carrying:
            for name in list(weights):
                if name != "inspect":
                    weights[name] *= 0.025
            weights["inspect"] = weights.get("inspect", 0.0) + 7.20
        elif intent_kind == "object_session" and intent_stage == "rumpled" and not carrying:
            for name in list(weights):
                if name not in {"loaf", "inspect"}:
                    weights[name] *= 0.025
            weights["loaf"] = weights.get("loaf", 0.0) + 7.00
        elif intent_kind == "object_session" and intent_stage in {"recovered", "nested"} and not carrying:
            for name in list(weights):
                if name not in {"idle", "rest", "loaf"}:
                    weights[name] *= 0.04
            weights["idle"] = weights.get("idle", 0.0) + 2.10
            weights["rest"] = weights.get("rest", 0.0) + 1.40
        elif intent_kind == "weather_reaction" and zone != "window":
            for name in list(weights):
                if name not in {"walk", "explore", "sleep"}:
                    weights[name] *= 0.025
            weights["walk"] = weights.get("walk", 0.0) + 7.00
            weights["explore"] = weights.get("explore", 0.0) * 0.10
            # Genuine exhaustion may still override curiosity, but ordinary
            # restlessness cannot break the reaction chain.
            weights["sleep"] = weights.get("sleep", 0.0) * 0.22
        elif intent_kind in {"event_recovery", "consequence_recovery"}:
            for name in list(weights):
                if name not in {"idle", "rest", "loaf", "stretch"}:
                    weights[name] *= 0.04
            weights["idle"] = weights.get("idle", 0.0) + 2.50
            weights["rest"] = weights.get("rest", 0.0) + 1.80

        adjusted: list[tuple[str, float]] = []
        movement_recent = sum(1 for a in recent[-3:] if a in {"walk", "explore"})
        manipulation_recent = sum(1 for a in recent[-4:] if a in {"carry", "place", "nudge"})
        for action_name, weight in weights.items():
            repeats = sum(1 for a in recent[-4:] if a == action_name)
            penalty = 1.0 if action_name == "sleep" else 0.52 ** repeats
            if action_name in {"walk", "explore"}:
                penalty *= 0.30 ** movement_recent
                penalty *= movement_context_penalty
            if action_name in {"carry", "place", "nudge"}:
                penalty *= 0.52 ** manipulation_recent
            adjusted.append((action_name, max(0.008, weight * penalty)))
        action = forced_action or self._weighted_pick(rng, adjusted)

        details: dict[str, Any] = {
            "from_zone": zone, "lighting": lighting, "weather": habitat["weather"],
            "decision": True, "intent_action": action,
        }
        event_type = "creature_activity"
        summary = "Moss is quietly awake."
        focus_object_id = None

        if action in {"walk", "explore"}:
            situational_travel = linked_event is not None and world_event_role in {"approach", "follow_affordance"} and linked_target is not None
            consequence_travel = intent_kind == "consequence_revisit" and consequence_role == "approach" and linked_consequence_id is not None
            if situational_travel:
                target = str(linked_target["zone"])
                destination = (int(linked_target["x"]), int(linked_target["y"]))
                if not point_is_walkable(destination):
                    destination = zone_anchor(target)
                details["supported_action"] = "situational_event_approach"
                details["target_x"], details["target_y"] = destination
            elif consequence_travel:
                target = str(intent.get("target_zone") or zone)
                destination = zone_anchor(target)
                details["supported_action"] = "consequence_revisit_approach"
                details["target_x"], details["target_y"] = destination
            else:
                target = self._choose_destination(rng, state, context, zone=zone, carrying=carrying, habit_profile=habit_profile)
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
                    record_consequence(
                        state, kind="persistent_trace", zone=target, strength=0.42,
                        source={"cause": "path_wear", "mark": mark, "wear_count": int(habitat["path_wear"][target])},
                        min_delay_minutes=180,
                    )
            self._remember_zone(context, target)
            if situational_travel and linked_event is not None:
                context["intent"] = {
                    "kind": "situational_event", "stage": "arrived", "event_id": linked_event["id"],
                    "event_type": linked_event["type"], "target_zone": target,
                }
                if world_event_role == "follow_affordance":
                    linked_event["follow_moves"] = int(linked_event.get("follow_moves", 0)) + 1
                travel_purpose = "situational_event"
            elif consequence_travel and linked_consequence_id is not None:
                context["intent"] = {
                    "kind": "consequence_revisit", "stage": "arrived", "memory_id": linked_consequence_id,
                    "target_zone": target, "object_id": intent.get("object_id"),
                    "engage_action": intent.get("engage_action"),
                }
                travel_purpose = "consequence_revisit"
            elif carrying:
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
        elif action == "inspect" and inspectable:
            obj = self._choose_object(
                rng, inspectable, context, habit_profile=habit_profile,
                preferred_id=(
                    str(intent_object_id)
                    if intent_object_id and (
                        (intent_kind == "object_session" and intent_stage in {"inspected", "rolled", "rumpled"})
                        or (intent_kind == "consequence_revisit" and intent_stage == "arrived")
                    )
                    else None
                ),
                required_affordance="inspect",
            )
            state_before = str(obj["interaction_state"])
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
            recovered = str(obj["archetype"]) == "rolling" and state_before == "rolled"
            if recovered:
                self._set_object_interaction_state(obj, "settled")
            details.update({
                "object_id": obj["id"], "target_x": target_x, "target_y": target_y,
                "object_archetype": obj["archetype"], "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                "object_affordance": "retrieve" if recovered else "inspect",
                "object_state_before": state_before, "object_state_after": obj["interaction_state"],
            })
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            next_stage = "recovered" if recovered else (
                "rumpled" if obj["archetype"] == "soft_nesting" and obj["interaction_state"] == "rumpled" else "inspected"
            )
            consequence_engagement = intent_kind == "consequence_revisit" and consequence_role == "engage" and linked_consequence_id is not None
            if consequence_engagement:
                mark_consequence_revisited(state, linked_consequence_id)
                context["intent"] = {"kind": "consequence_recovery", "stage": "settle", "memory_id": linked_consequence_id}
            else:
                context["intent"] = {"kind": "object_session", "stage": next_stage, "object_id": obj["id"]}
            event_type = "object_retrieved" if recovered else "object_inspected"
            summary = (
                f"Moss chased down the {obj['name'].lower()} after its roll and recovered it."
                if recovered else f"Moss stopped to inspect the {obj['name'].lower()}."
            )
            if consequence_engagement:
                summary = f"Moss returned to the {obj['name'].lower()} and inspected the consequence left there earlier."
        elif action == "carry" and carryable:
            obj = self._choose_object(
                rng, carryable, context, habit_profile=habit_profile,
                preferred_id=(str(intent_object_id) if intent_kind == "object_session" and intent_stage == "inspected" and intent_object_id else None),
                required_affordance="carry",
            )
            state_before = str(obj["interaction_state"])
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
            if obj["archetype"] == "soft_nesting":
                self._set_object_interaction_state(obj, "loose")
            elif obj["archetype"] == "rolling":
                self._set_object_interaction_state(obj, "settled")
            elif obj["archetype"] in {"keepsake", "delicate"}:
                self._set_object_interaction_state(obj, "handled")
            obj["x"] = int(creature["x"]) + (-22 if creature["facing"] == "left" else 22)
            obj["y"] = int(creature["y"]) - 4
            details.update({
                "object_id": obj["id"], "target_x": target_x, "target_y": target_y,
                "object_archetype": obj["archetype"], "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                "object_affordance": "carry", "object_state_before": state_before, "object_state_after": obj["interaction_state"],
            })
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            delivery_target = self._choose_arrangement_destination(
                rng, state, zone=zone, object_id=str(obj["id"]), habit_profile=habit_profile
            )
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
            state_before = str(obj["interaction_state"])
            if obj["archetype"] == "keepsake":
                self._set_object_interaction_state(obj, "displayed" if zone == "collection_shelf" else "handled")
            elif obj["archetype"] == "delicate":
                self._set_object_interaction_state(obj, "fresh" if zone == "window" else "handled")
            elif obj["archetype"] == "rolling":
                self._set_object_interaction_state(obj, "settled")
            elif obj["archetype"] == "soft_nesting":
                self._set_object_interaction_state(obj, "loose")
            obj["times_moved"] = int(obj["times_moved"]) + 1
            aftermath["arrangement_places"] = int(aftermath["arrangement_places"]) + 1
            creature["carrying"] = None
            creature["activity"] = "place"
            creature["expression"] = "content"
            details.update({
                "object_id": obj["id"], "to_zone": zone, "x": obj["x"], "y": obj["y"], "target_x": target_x, "target_y": target_y,
                "object_archetype": obj["archetype"], "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                "object_affordance": "display" if obj["interaction_state"] == "displayed" else "place",
                "object_state_before": state_before, "object_state_after": obj["interaction_state"],
            })
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            context["intent"] = {"kind": "post_place", "stage": "settle", "object_id": obj["id"], "zone": zone}
            record_consequence(
                state, kind="object_arrangement", zone=zone, object_id=str(obj["id"]), strength=0.62,
                source={
                    "cause": "object_placed", "object_affordance": details["object_affordance"],
                    "object_state": str(obj["interaction_state"]), "times_moved": int(obj["times_moved"]),
                },
                min_delay_minutes=120,
            )
            event_type = "object_placed"
            summary = f"Moss placed the {obj['name'].lower()} in the {zone.replace('_', ' ')} and regarded it for a moment."
        elif action == "nudge" and nudgeable:
            obj = self._choose_object(
                rng, nudgeable, context, habit_profile=habit_profile,
                preferred_id=(str(intent_object_id) if intent_object_id else None), required_affordance="nudge",
            )
            state_before = str(obj["interaction_state"])
            old_x, old_y = int(obj["x"]), int(obj["y"])
            approach = interaction_approach(zone=zone, target_x=old_x, target_y=old_y, current_x=int(creature["x"]), current_y=int(creature["y"]))
            self._route_creature(creature, details, destination=approach, destination_zone=zone)
            contact = interaction_contact(zone=zone, target_x=old_x, target_y=old_y, approach=approach)
            details["contact_x"], details["contact_y"] = contact
            creature["facing"] = "right" if contact[0] >= int(creature["x"]) else "left"
            new_x, new_y = self._nudge_position(state, obj)
            obj["x"], obj["y"] = new_x, new_y
            if obj["archetype"] == "rolling":
                affordance_name, next_stage = "roll", "rolled"
                self._set_object_interaction_state(obj, "rolled")
            elif obj["archetype"] == "soft_nesting":
                affordance_name, next_stage = "tug", "rumpled"
                self._set_object_interaction_state(obj, "rumpled")
            else:
                raise AssertionError(f"object {obj['id']} reached nudge without a play affordance")
            obj["times_nudged"] = int(obj.get("times_nudged", 0)) + 1
            obj["times_moved"] = int(obj["times_moved"]) + 1
            aftermath["object_nudges"] = int(aftermath["object_nudges"]) + 1
            creature["activity"] = "nudge"
            creature["expression"] = "excited"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.055)
            details.update({
                "object_id": obj["id"], "target_x": old_x, "target_y": old_y,
                "result_x": new_x, "result_y": new_y, "to_zone": zone,
                "object_archetype": obj["archetype"], "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                "object_affordance": affordance_name, "object_state_before": state_before,
                "object_state_after": obj["interaction_state"],
            })
            focus_object_id = obj["id"]
            self._remember_object(context, obj["id"])
            context["intent"] = {"kind": "object_session", "stage": next_stage, "object_id": obj["id"], "zone": zone}
            record_consequence(
                state, kind="object_displacement", zone=zone, object_id=str(obj["id"]), strength=0.68,
                source={
                    "cause": "object_interaction", "object_affordance": affordance_name,
                    "object_state": str(obj["interaction_state"]), "from_x": old_x, "from_y": old_y,
                    "to_x": new_x, "to_y": new_y,
                },
                min_delay_minutes=150,
            )
            event_type = "object_rolled" if affordance_name == "roll" else "object_tugged"
            summary = (
                f"Moss pawed the {obj['name'].lower()} into a roll and watched where it went."
                if affordance_name == "roll"
                else f"Moss tugged the {obj['name'].lower()} into a rumpled little nest shape."
            )
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
        elif action == "loaf" and intent_kind == "object_session" and intent_stage == "rumpled" and intent_object_id:
            obj = next((o for o in nearby if o["id"] == intent_object_id and "nest" in object_affordances(o)), None)
            if obj is None:
                context["intent"] = None
                creature["activity"] = "loaf"
                creature["expression"] = "content"
                event_type = "creature_loafed"
                summary = f"Moss tucked into a comfortable loaf in the {zone.replace('_', ' ')}."
            else:
                state_before = str(obj["interaction_state"])
                approach = interaction_approach(
                    zone=zone, target_x=int(obj["x"]), target_y=int(obj["y"]),
                    current_x=int(creature["x"]), current_y=int(creature["y"]),
                )
                self._route_creature(creature, details, destination=approach, destination_zone=zone)
                self._set_object_interaction_state(obj, "nested")
                creature["activity"] = "loaf"
                creature["expression"] = "content"
                creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.045)
                aftermath["loaf_sessions"] = int(aftermath["loaf_sessions"]) + 1
                focus_object_id = obj["id"]
                details.update({
                    "object_id": obj["id"], "target_x": int(obj["x"]), "target_y": int(obj["y"]),
                    "object_archetype": obj["archetype"], "object_affordance_schema": OBJECT_AFFORDANCE_SCHEMA,
                    "object_affordance": "nest", "object_state_before": state_before,
                    "object_state_after": obj["interaction_state"], "supported_action": "object_nest",
                })
                context["intent"] = {"kind": "object_session", "stage": "nested", "object_id": obj["id"], "zone": zone}
                record_consequence(
                    state, kind="object_nest", zone=zone, object_id=str(obj["id"]), strength=0.74,
                    source={"cause": "object_nested", "object_state": str(obj["interaction_state"])},
                    min_delay_minutes=180,
                )
                event_type = "object_nested"
                summary = f"Moss settled onto the rumpled {obj['name'].lower()} and made it into a temporary nest."
        elif action == "loaf":
            sunlight_engagement = linked_event is not None and linked_event.get("type") == "sunlight" and world_event_role == "engage" and linked_target is not None
            if sunlight_engagement:
                destination = (int(linked_target["x"]), int(linked_target["y"]))
                if (int(creature["x"]), int(creature["y"])) != destination:
                    self._route_creature(creature, details, destination=destination, destination_zone="open_space")
                details["supported_action"] = "sunlight_affordance"
                details["target_x"], details["target_y"] = destination
            else:
                spot = next((spot for spot in FAVORITE_SPOTS.values() if spot["zone"] == zone), None)
                if spot is not None:
                    self._route_creature(creature, details, destination=(int(spot["x"]), int(spot["y"])), destination_zone=zone)
                    details["supported_action"] = "comfort_spot"
            creature["activity"] = "loaf"
            creature["expression"] = "content"
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.035)
            aftermath["loaf_sessions"] = int(aftermath["loaf_sessions"]) + 1
            if sunlight_engagement and linked_event is not None:
                mark_engaged(state, linked_event)
                context["intent"] = {
                    "kind": "situational_event", "stage": "engaged", "event_id": linked_event["id"],
                    "event_type": linked_event["type"], "target_zone": "open_space",
                }
                event_type = "sunlight_used"
                summary = "Moss settled into the temporary patch of sunlight on the rug."
            elif intent_kind == "consequence_revisit" and consequence_role == "engage" and linked_consequence_id is not None:
                mark_consequence_revisited(state, linked_consequence_id)
                context["intent"] = {"kind": "consequence_recovery", "stage": "settle", "memory_id": linked_consequence_id}
                event_type = "creature_loafed"
                summary = f"Moss returned to the {zone.replace('_', ' ')} and settled beside a consequence from earlier activity."
            else:
                if intent_kind in {"arrival_settle", "post_place", "wake_recovery", "event_recovery", "consequence_recovery"}:
                    context["intent"] = None
                event_type = "creature_loafed"
                summary = f"Moss tucked into a comfortable loaf in the {zone.replace('_', ' ')}."
        elif action == "groom":
            creature["activity"] = "groom"
            creature["expression"] = "content"
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.026)
            aftermath["groom_sessions"] = int(aftermath["groom_sessions"]) + 1
            event_type = "creature_groomed"
            summary = "Moss stopped for a slow grooming session."
        elif action == "stretch":
            creature["activity"] = "stretch"
            creature["expression"] = "content"
            creature["comfort"] = min(1.0, float(creature["comfort"]) + 0.018)
            aftermath["stretch_sessions"] = int(aftermath["stretch_sessions"]) + 1
            if intent_kind in {"wake_recovery", "event_recovery", "consequence_recovery"}:
                context["intent"] = None
            event_type = "creature_stretched"
            summary = "Moss leaned into a long stretch and settled back down."
        elif action == "react":
            creature["activity"] = "react"
            creature["expression"] = "startled" if linked_event is not None and linked_event.get("type") == "thunder" else "curious"
            if intent_kind == "consequence_revisit":
                consequence_zone = str(intent.get("target_zone") or zone)
                face_x = int(zone_anchor(consequence_zone)[0])
            else:
                face_x = int(linked_target["x"]) if linked_target is not None else int(ZONES["window"]["x"])
            creature["facing"] = "left" if int(creature["x"]) > face_x else "right"
            creature["curiosity"] = max(0.0, float(creature["curiosity"]) - 0.025)
            if intent_kind == "consequence_revisit" and consequence_role == "recognize" and linked_consequence_id is not None:
                event_type = "consequence_recognized"
                summary = "Moss paused as a consequence of earlier activity became relevant again."
            elif linked_event is not None and world_event_role in {"notice", "notice_after_defer", "notice_after_interrupt", "orient", "engage"}:
                if world_event_role == "orient":
                    context["intent"] = None
                    event_type = "world_event_oriented"
                    summary = f"Moss briefly oriented toward the {str(linked_event['type']).replace('_', ' ')} and then held its course."
                elif world_event_role == "engage":
                    mark_engaged(state, linked_event)
                    context["intent"] = {"kind": "event_recovery", "stage": "settle", "event_type": linked_event["type"]}
                    event_type = "world_event_engaged"
                    summary = f"Moss tracked the {str(linked_event['type']).replace('_', ' ')} for a bounded moment, then began to settle."
                else:
                    event_type = "world_event_noticed"
                    summary = f"Moss noticed the {str(linked_event['type']).replace('_', ' ')} and turned its attention toward it."
            else:
                aftermath["weather_reactions"] = int(aftermath["weather_reactions"]) + 1
                (habitat.get("affordance_history") or {})["last_weather_reaction_block"] = int(state["world_minutes"]) // 180
                context["intent"] = {"kind": "weather_reaction", "stage": "noticed", "target_zone": "window"}
                event_type = "weather_noticed"
                summary = f"Moss noticed the {habitat['weather']} outside and turned its attention toward the window."
        elif action == "rest":
            creature["activity"] = "rest"
            creature["expression"] = "content"
            creature["energy"] = min(1.0, float(creature["energy"]) + 0.034)
            if intent_kind == "consequence_revisit" and consequence_role == "engage" and linked_consequence_id is not None:
                mark_consequence_revisited(state, linked_consequence_id)
                context["intent"] = {"kind": "consequence_recovery", "stage": "settle", "memory_id": linked_consequence_id}
                summary = f"Moss returned to the {zone.replace('_', ' ')} and rested near a familiar consequence."
            elif intent_kind in {"arrival_settle", "post_place", "wake_recovery", "event_recovery", "consequence_recovery"} or (
                intent_kind == "object_session" and intent_stage in {"recovered", "nested"}
            ):
                context["intent"] = None
            elif intent_kind == "window_session" and intent_stage != "arrived":
                context["intent"] = None
            event_type = "creature_rested"
            if not (intent_kind == "consequence_revisit" and consequence_role == "engage"):
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
            if linked_event is not None and world_event_role == "engage":
                mark_engaged(state, linked_event)
                context["intent"] = {"kind": "event_recovery", "stage": "settle", "event_type": linked_event["type"]}
                event_type = "world_event_watched"
                summary = f"Moss watched the {str(linked_event['type']).replace('_', ' ')} from the window until the moment passed."
            elif intent_kind == "consequence_revisit" and consequence_role == "engage" and linked_consequence_id is not None:
                mark_consequence_revisited(state, linked_consequence_id)
                context["intent"] = {"kind": "consequence_recovery", "stage": "settle", "memory_id": linked_consequence_id}
                event_type = "window_watched"
                summary = "Moss returned to the window and watched the place where an earlier consequence still mattered."
            else:
                context["intent"] = {"kind": "window_session", "stage": "watched", "zone": "window"}
                event_type = "window_watched"
                summary = f"Moss watched the {habitat['weather']} outside the window."
        else:
            creature["activity"] = "idle"
            creature["expression"] = "neutral"
            if intent_kind in {"arrival_settle", "post_place", "wake_recovery", "event_recovery", "consequence_recovery"} or (
                intent_kind == "object_session" and intent_stage in {"recovered", "nested"}
            ):
                context["intent"] = None
            elif intent_kind == "window_session" and intent_stage != "arrived":
                context["intent"] = None
            event_type = "creature_idled"
            summary = f"Moss lingered in the {zone.replace('_', ' ')}."

        if zone == "activity_corner" and action in {"idle", "rest", "loaf", "groom", "stretch", "inspect", "nudge", "carry", "place"}:
            aftermath["activity_corner_uses"] = int(aftermath["activity_corner_uses"]) + 1
        activity_family = self._record_affordance(
            state, action=action, zone=str(creature["zone"]), object_id=str(focus_object_id) if focus_object_id else None
        )
        details["activity_family"] = activity_family
        details["affordance_schema"] = AFFORDANCE_HISTORY_SCHEMA
        details["object_affordance_schema"] = OBJECT_AFFORDANCE_SCHEMA
        self._learn_from_decision(
            state,
            action=action,
            zone=str(creature["zone"]),
            object_id=str(focus_object_id) if focus_object_id else None,
            lighting=str(habitat["lighting"]),
        )
        details["habit_schema"] = HABIT_PROFILE_SCHEMA
        details["habit_experience_count"] = int(habit_profile["experience_count"])
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
        details["season"] = season_now["season"]
        details["season_stage"] = season_now["stage"]
        if season_before.get("season") != season_now["season"] or season_before.get("stage") != season_now["stage"]:
            details["season_transition"] = {"from_season": season_before.get("season"), "from_stage": season_before.get("stage"), "to_season": season_now["season"], "to_stage": season_now["stage"]}
        self._annotate_situation(details, state, event_transition, event=linked_event, role=world_event_role, preempted_action=preempted_action)
        self._annotate_consequence(details, state, role=consequence_role, memory_id=linked_consequence_id)
        return event_type, summary, details, state


class WorldEngine:
    def __init__(self, store: WorldStore, *, seed: int = 1701, minutes_per_tick: int = 1, snapshot_every: int = 20, real_time_seasons: bool = False):
        self.store = store
        self.state = store.initialize(seed)
        self.simulation = Simulation(minutes_per_tick=minutes_per_tick)
        self.snapshot_every = int(snapshot_every)
        self.real_time_seasons = bool(real_time_seasons)
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def step(self, *, observed_at_utc: str | None = None) -> dict[str, Any]:
        with self._lock:
            before = self.state
            observed = observed_at_utc if observed_at_utc is not None else (utc_now() if self.real_time_seasons else None)
            event_type, summary, details, next_state = self.simulation.step(before, observed_at_utc=observed)
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
