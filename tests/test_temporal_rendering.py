from __future__ import annotations

import importlib.util
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
        "sleep_transition", "window_transition", "activity_corner_transition",
        "object_placement", "rain_control",
    }
    for scenario in first["scenarios"].values():
        for frame in (scenario["source"], scenario["target"]):
            assert (frame["logical_width"], frame["logical_height"]) == (800, 480)


def test_window_semantic_anchor_matches_sill_side_contact_space():
    y = ZONES["window"]["y"]
    placement_ys = [slot_y for _, slot_y in PLACEMENT_SLOTS["window"]]
    assert y == 277
    assert min(placement_ys) - 20 <= y <= max(placement_ys) + 20


def test_temporal_tooling_is_development_gated_by_default():
    args = build_parser().parse_args([])
    assert args.dev_temporal_fixtures is None
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
    assert "drawForegroundCausality(frame, now, renderState)" in source
