from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_temporal_fixture_pack import build
REQUIRED_REVIEW = {
    "quiet_clear_day", "quiet_clear_night", "night_with_warm_local_lighting", "rain", "mist",
    "window_focused", "moss_stationary_environment_alive", "moss_walking_atmosphere_subordinate",
    "situational_event_plus_ambient", "sleep_context", "object_interaction",
}
AMBIENT_ASSETS = {
    "environment.window-foliage-far", "environment.window-foliage-mid", "environment.window-foliage-near",
    "environment.window-curtain-motion", "environment.nook-sconce",
}


def evaluate() -> dict[str, Any]:
    first = build()
    second = build()
    manifest = json.loads((ROOT / "display/art/manifest.json").read_text(encoding="utf-8"))
    palette = json.loads((ROOT / "display/art/palettes/materials.json").read_text(encoding="utf-8"))
    js = (ROOT / "display/web/app.js").read_text(encoding="utf-8")
    ids = {entry["id"] for entry in manifest["assets"]}
    periods = [int(v) for v in re.findall(r"ambientStep\(clock,(\d+)", js)]
    rain_match = re.search(r"period:(\d+)\+\(i%6\)\*(\d+)", js)
    rain_periods = [] if rain_match is None else [int(rain_match.group(1)) + i * int(rain_match.group(2)) for i in range(6)]
    atmosphere_names = set(first.get("atmosphere_review", {}).values())
    semantic_stationary = True
    for name in atmosphere_names:
        scenario = first["scenarios"][name]
        if scenario.get("temporal_kind") != "atmosphere": semantic_stationary = False
        if name.endswith("idle") or name in {"atmosphere_night_warm_light", "atmosphere_window_focus"}:
            src, dst = scenario["source"], scenario["target"]
            semantic_stationary &= src["creature"]["x"] == dst["creature"]["x"] and src["creature"]["y"] == dst["creature"]["y"]
    checks = {
        "fixture_pack_exact_repeat": first == second,
        "all_required_review_contexts_present": set(first.get("atmosphere_review", {})) == REQUIRED_REVIEW,
        "long_observation_reaches_56_seconds": max(first.get("atmosphere_timestamps_ms", [0])) >= 56000,
        "ambient_scenarios_are_explicit": all(first["scenarios"][name].get("temporal_kind") == "atmosphere" for name in atmosphere_names),
        "quiet_controls_preserve_semantic_position": bool(semantic_stationary),
        "authored_ambient_assets_present": AMBIENT_ASSETS <= ids,
        "whole_scene_weather_treatments_present": set(palette.get("weather_treatments", {})) == {"rain", "mist"},
        "local_light_palette_treatment_present": bool(palette.get("local_light_treatment")),
        "phase_periods_are_not_one_global_loop": len(set(periods)) >= 5,
        "rain_traces_have_multiple_periods": len(set(rain_periods)) >= 4,
        "ambient_motion_uses_canonical_time": "worldMinuteAt(f,now)*3000" in js,
        "no_behavior_authority_added": "ambient_control" not in (ROOT / "terrarium/engine.py").read_text(encoding="utf-8"),
        "no_random_or_sine_motion": "Math.random" not in js and "Math.sin" not in js and "Math.cos" not in js,
        "no_soft_modern_compositing": all(token not in js for token in ("createLinearGradient", "createRadialGradient", "globalAlpha", "shadowBlur", "ctx.filter", "displayCtx.filter", "rgba(")),
        "ambient_presentation_is_below_actor_layer": "scene.add('WORLD',0,'world-atmosphere'" in js and "scene.add('ACTORS'" in js,
    }
    return {
        "schema": "terrarium.atmosphere-evaluation.v1",
        "passed": all(checks.values()),
        "checks": checks,
        "ambient_assets": sorted(AMBIENT_ASSETS),
        "authored_asset_count": len(manifest["assets"]),
        "atmosphere_scenarios": sorted(atmosphere_names),
        "observation_timestamps_ms": first["atmosphere_timestamps_ms"],
        "ambient_periods_ms": sorted(set(periods)),
        "rain_trace_periods_ms": sorted(set(rain_periods)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/pixel-art-overhaul-iteration8e-atmosphere.json")
    args = parser.parse_args()
    result = evaluate()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
