from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from terrarium.api.server import build_parser
from terrarium.models import PLACEMENT_SLOTS, ZONES

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name: str):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_temporal_fixture_pack_is_deterministic_and_800x480():
    tool = load_tool("build_temporal_fixture_pack")
    first = tool.build()
    second = tool.build()
    assert first == second
    assert set(first["scenarios"]) == {
        "arrive_settle", "left_walk", "right_walk", "carried_walk", "idle_control",
        "sleep_transition", "waking", "wake_exit", "window_transition", "activity_corner_transition",
        "activity_corner_approach", "shelf_approach", "inspect_object", "object_nudge", "object_pickup", "object_placement", "rain_window",
        "loaf", "groom", "stretch", "weather_reaction",
        "populated_room", "event_sunlight_engage", "event_bird_engage", "event_thunder_react", "event_moth_engage", "event_ignored",
        "dawn_light_transition", "dusk_light_transition", "rain_control",
    }
    assert first["hero_reel"] == [
        "left_walk", "right_walk", "arrive_settle", "idle_control", "window_transition",
        "rain_window", "weather_reaction", "inspect_object", "object_nudge", "object_pickup", "carried_walk", "object_placement",
        "loaf", "groom", "stretch", "sleep_transition", "waking", "wake_exit", "activity_corner_approach", "activity_corner_transition",
        "shelf_approach", "populated_room", "event_sunlight_engage", "event_bird_engage", "event_thunder_react", "event_moth_engage", "event_ignored",
        "dawn_light_transition", "dusk_light_transition", "rain_control",
    ]
    probe = first["continuity_probe"]
    assert probe["source"]["tick"] < probe["middle"]["tick"] < probe["followup"]["tick"]
    for scenario in first["scenarios"].values():
        for frame in (scenario["source"], scenario["target"]):
            assert (frame["logical_width"], frame["logical_height"]) == (800, 480)


def test_window_semantic_anchor_is_floor_side_of_window_objects():
    y = ZONES["window"]["y"]
    placement_ys = [slot_y for _, slot_y in PLACEMENT_SLOTS["window"]]
    assert y == 316
    assert max(placement_ys) < y
    assert y - max(placement_ys) <= 50


def test_temporal_tooling_is_development_gated_by_default():
    args = build_parser().parse_args([])
    assert args.dev_temporal_fixtures is None
    assert args.minutes_per_tick == 1
    assert args.dev_temporal_output_dir is None


def test_renderer_has_manual_clock_path_and_production_raf_path():
    source = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    assert "function creatureRenderState(f, now)" in source
    assert "async function captureTemporalSample(timestamp)" in source
    assert "function render(now, scheduleNext = true)" in source
    assert "requestAnimationFrame(render)" in source
    assert "Math.random" not in source
    assert "smoother01" in source and "temporalRafProbe" in source
    assert "function causalActivityState(f, now)" in source
    assert "function placedObjectRenderState(o, f, now)" in source
    assert "function acceptFrame(next, now)" in source
    assert "function authoredRoute(f,sourceX,sourceY)" in source
    assert "function routeSample(points,progress)" in source
    assert "route_distance" in source and "route_segment_index" in source
    assert "transitionSource" in source and "temporalContinuityProbe" in source
    assert "drawForegroundCausality(frame,now,renderState" in source or "drawForegroundCausality(frame, now, renderState" in source
    assert "function worldEventRenderState" in source
    assert "drawFloorWorldEvent" in source and "drawWindowWorldEvent" in source and "drawInteriorWorldEvent" in source
    assert all(name in source for name in ("sunlight", "bird", "rain_intensify", "thunder", "moth", "leaf_tap"))


def test_renderer_is_pixel_native_400x240_with_exact_2x_present_path():
    source = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    assert "const ART_W = 400" in source and "const ART_H = 240" in source
    assert "const SCALE = 2" in source
    assert "artCanvas.width = ART_W" in source and "artCanvas.height = ART_H" in source
    assert "displayCtx.imageSmoothingEnabled = false" in source
    assert "ctx.imageSmoothingEnabled = false" in source
    assert "displayCtx.drawImage(artCanvas,0,0,ART_W,ART_H,0,0,DISPLAY_W,DISPLAY_H)" in source
    assert "scale2x_exact" in source and "scale2x_error_blocks" in source
    assert "window.__terrariumPixelRenderer" in source
    assert "createRadialGradient" not in source
    assert "roundRect" not in source
    assert "ctx.ellipse" not in source


def test_moss_pixel_sprite_is_brown_and_default_has_no_glasses():
    source = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    palettes = json.loads((ROOT / "display" / "art" / "palettes" / "materials.json").read_text(encoding="utf-8"))
    assert palettes["palettes"]["day"]["dog"] == "#8b5d3b"
    assert "function drawMossSprite" in source
    assert "pose==='walk'" in source and "pose==='sleep'" in source
    assert "pose==='inspect'" in source and "pose==='nudge'" in source and "pose==='carry'" in source and "pose==='place'" in source
    assert "pose==='loaf'" in source and "pose==='groom'" in source and "pose==='stretch'" in source and "pose==='react'" in source
    assert "pose==='window'" in source and "c.activity==='wake'" in source
    assert "glasses" not in source.lower()
