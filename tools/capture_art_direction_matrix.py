from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrarium.engine import Simulation
from terrarium.frame import make_frame
from terrarium.models import initial_state, lighting_for
from tools.build_temporal_fixture_pack import build as build_temporal_pack

CREATED_AT = "2026-01-01T00:00:00Z"


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_json(value: object) -> str:
    return _sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _sha_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _static_scenario(name: str, *, minute: int, weather: str, lived_steps: int = 0) -> dict[str, Any]:
    state = initial_state(1701, created_at=CREATED_AT)
    if lived_steps:
        sim = Simulation()
        for _ in range(lived_steps):
            _, _, _, state = sim.step(state)
    state = deepcopy(state)
    state["world_minutes"] = minute
    state["habitat"]["lighting"] = lighting_for(minute)
    state["habitat"]["weather"] = weather
    state["creature"]["activity"] = "idle"
    state["creature"]["pose"] = "standing"
    frame = make_frame(
        state,
        last_event={
            "event_id": f"fixture-{name}",
            "type": "fixture",
            "summary": "Deterministic art-direction matrix control.",
            "details": {
                "action": "art_direction_control",
                "decision": False,
                "from_zone": state["creature"]["zone"],
                "to_zone": state["creature"]["zone"],
            },
        },
    )
    return {
        "id": name,
        "seed": 1701,
        "source_tick": frame["tick"],
        "target_tick": frame["tick"],
        "source": frame,
        "target": deepcopy(frame),
        "semantic_event": {"action": "art_direction_control", "from_zone": frame["creature"]["zone"], "to_zone": frame["creature"]["zone"]},
        "purpose": f"art review: {lighting_for(minute)} / {weather} / {'lived-in' if lived_steps else 'fresh'}",
    }


def build_matrix() -> tuple[dict[str, Any], dict[str, Any]]:
    base = build_temporal_pack()
    scenarios: dict[str, dict[str, Any]] = {
        "art_dawn_clear_fresh_idle": _static_scenario("art_dawn_clear_fresh_idle", minute=390, weather="clear"),
        "art_day_clear_fresh_idle": _static_scenario("art_day_clear_fresh_idle", minute=720, weather="clear"),
        "art_dusk_mist_fresh_idle": _static_scenario("art_dusk_mist_fresh_idle", minute=1110, weather="mist"),
        "art_night_rain_fresh_idle": _static_scenario("art_night_rain_fresh_idle", minute=1230, weather="rain"),
        "art_day_clear_lived_idle": _static_scenario("art_day_clear_lived_idle", minute=720, weather="clear", lived_steps=480),
        "art_night_rain_lived_idle": _static_scenario("art_night_rain_lived_idle", minute=1230, weather="rain", lived_steps=480),
    }
    borrowed = [
        "left_walk", "right_walk", "inspect_object", "object_nudge", "object_pickup", "carried_walk", "object_placement",
        "loaf", "groom", "stretch", "weather_reaction", "window_transition", "sleep_transition", "waking", "wake_exit",
        "event_sunlight_engage", "event_bird_engage", "event_thunder_react", "event_moth_engage",
    ]
    for name in borrowed:
        scenarios[name] = base["scenarios"][name]

    fixture_pack = {
        "schema": base["schema"],
        "transition_duration_ms": base["transition_duration_ms"],
        "recommended_timestamps_ms": base["recommended_timestamps_ms"],
        "hero_reel": list(scenarios),
        "continuity_probe": base["continuity_probe"],
        "scenarios": scenarios,
    }
    rows = [
        {"group": "environment", "scenarios": ["art_dawn_clear_fresh_idle", "art_day_clear_fresh_idle", "art_dusk_mist_fresh_idle", "art_night_rain_fresh_idle"]},
        {"group": "history", "scenarios": ["art_day_clear_fresh_idle", "art_day_clear_lived_idle", "art_night_rain_fresh_idle", "art_night_rain_lived_idle"]},
        {"group": "moss-locomotion", "scenarios": ["art_day_clear_fresh_idle", "left_walk", "right_walk", "carried_walk"]},
        {"group": "moss-object-acting", "scenarios": ["inspect_object", "object_nudge", "object_pickup", "object_placement"]},
        {"group": "moss-quiet-acting", "scenarios": ["loaf", "groom", "stretch", "window_transition", "sleep_transition", "waking", "wake_exit"]},
        {"group": "situations", "scenarios": ["weather_reaction", "event_sunlight_engage", "event_bird_engage", "event_thunder_react", "event_moth_engage"]},
    ]
    renderer_path = ROOT / "display" / "web" / "app.js"
    renderer_sha = _sha_bytes(renderer_path.read_bytes())
    art_sha = _sha_tree(ROOT / "display" / "art")
    manifest = {
        "schema": "terrarium.art-direction-matrix.v1",
        "renderer": "production display/web/app.js",
        "renderer_sha256": renderer_sha,
        "authored_art_sha256": art_sha,
        "viewport": [800, 480],
        "art_surface": [400, 240],
        "capture_rule": "start the development server with the generated fixture pack, then capture each URL from the production browser renderer at 800x480; subjective visual judgment remains human/vision authority",
        "rows": rows,
        "captures": {name: {"url": f"/?temporal={name}&t=1300", "target_frame_sha256": _sha_json(scenario["target"])} for name, scenario in scenarios.items()},
    }
    return fixture_pack, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic production-renderer fixtures for Terrarium art-direction review.")
    parser.add_argument("--fixtures", default="artifacts/iteration8a-art-direction-fixtures.json")
    parser.add_argument("--manifest", default="artifacts/iteration8a-art-direction-matrix.json")
    args = parser.parse_args()
    fixtures, manifest = build_matrix()
    fixture_path = Path(args.fixtures)
    manifest_path = Path(args.manifest)
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps(fixtures, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"fixtures": str(fixture_path), "manifest": str(manifest_path), "scenarios": len(fixtures["scenarios"]), "schema": manifest["schema"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
