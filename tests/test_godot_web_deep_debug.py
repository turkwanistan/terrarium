from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from tools.build_godot_web_debug_fixtures import build
from tools.godot_web_fixture_server import FixtureState, load_frames

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "display" / "godot_reference_v2"


def test_web_debug_fixture_pack_is_valid_deterministic_and_complete(tmp_path: Path) -> None:
    one = tmp_path / "one.json"
    two = tmp_path / "two.json"
    tool = ROOT / "tools" / "build_godot_web_debug_fixtures.py"
    for output in (one, two):
        result = subprocess.run(
            [sys.executable, str(tool), "--output", str(output)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
    assert hashlib.sha256(one.read_bytes()).digest() == hashlib.sha256(two.read_bytes()).digest()
    payload = json.loads(one.read_text())
    assert payload["schema"] == "terrarium.godot-web-debug-fixtures.v1"
    assert payload["recommended_browser_query"] == "?terrarium_debug=1&terrarium_poll_ms=300"
    frames = payload["sequences"]["composite"]
    assert len(frames) >= 90
    assert all(frame["schema"] == "terrarium.frame.v1" for frame in frames)
    assert all((frame["logical_width"], frame["logical_height"]) == (800, 480) for frame in frames)
    activities = {frame["creature"]["activity"] for frame in frames}
    assert {
        "idle", "walk", "inspect", "nudge", "groom", "stretch", "loaf", "rest",
        "react", "look_outside", "carry", "place", "sleep", "wake",
    } <= activities
    ticks = [int(frame["tick"]) for frame in frames]
    assert any(a == b for a, b in zip(ticks, ticks[1:]))
    assert any(b < a for a, b in zip(ticks, ticks[1:]))
    assert any(frame["weather"] == "rain" for frame in frames)
    assert any(frame.get("lighting") == "night" for frame in frames)
    assert any(frame["creature"].get("carrying") is not None for frame in frames)


def test_web_debug_fixture_state_advances_then_holds_last_frame(tmp_path: Path) -> None:
    payload = build()
    fixture_path = tmp_path / "fixtures.json"
    fixture_path.write_text(json.dumps(payload))
    frames = load_frames(fixture_path, "composite")
    state = FixtureState(frames[:3])
    seen = [state.next_frame()[1]["tick"] for _ in range(5)]
    assert seen[:3] == [frame["tick"] for frame in frames[:3]]
    assert seen[3:] == [frames[2]["tick"], frames[2]["tick"]]
    assert state.status()["requests"] == 5
    assert state.status()["complete"] is True


def test_live_route_rebases_only_for_new_targets_and_uses_authoritative_route_evidence() -> None:
    main = (REFERENCE / "scripts" / "main.gd").read_text()
    assert "var rendered_before := _current_rendered_anchor() if had_live_frame else _map_live_position(creature)" in main
    assert "var position_changed := not had_live_frame or next_position.distance_to(live_position) > 0.01" in main
    assert "elif position_changed:" in main
    assert "live_route_points = _build_live_route(frame, rendered_before, true, next_motion)" in main
    assert "Same-position continuation heartbeats intentionally leave route and transition clock" in main
    assert "result.append(rendered_start)" in main
    assert 'typeof(event.get("route", [])) == TYPE_ARRAY' in main
    assert 'if motion_name == "sleep" and route_limit >= 2:' in main
    assert "LIVE_ACTOR_ANCHOR_OFFSET" in main
    assert "live_transition_duration_ms = _transition_duration_for_interval" in main
    assert "LIVE_TRANSITION_INTERVAL_FRACTION := 0.90" in main
    assert "LIVE_TRANSITION_MIN_MS := 450.0" in main
    assert "LIVE_TRANSITION_MAX_MS := 2800.0" in main
    assert "t * t * t * (t * (t * 6.0 - 15.0) + 10.0)" in main


def test_support_and_carried_travel_phases_preserve_continuity() -> None:
    main = (REFERENCE / "scripts" / "main.gd").read_text()
    assert 'if travel_active and motion != "walk":' in main
    assert 'rendered_motion = "walk"' in main
    assert 'var attached_travel := rendered_motion == "walk"' in main
    assert 'action_object.visible = rendered_motion in ["carry", "place"] or attached_travel' in main
    assert 'if rendered_motion == "carry" or attached_travel:' in main
    assert "LIVE_SUPPORT_TRANSITION_MS := 450.0" in main
    assert 'live_previous_motion != "window_watch"' in main
    assert 'live_previous_motion == "window_watch" and motion != "window_watch"' in main
    assert "live_motion_entry_actor_position" in main
    assert "sleep action itself presents the final supported move inward" in main

def test_animation_lifetime_has_continuation_safe_sustain_and_recovery_phases() -> None:
    main = (REFERENCE / "scripts" / "main.gd").read_text()
    assert '"inspect": [1, 2]' in main
    assert '"nudge": [2, 3]' in main
    assert '"groom": [1, 2]' in main
    assert '"stretch": [1, 2]' in main
    assert "MOTION_START_FRAME_COUNTS" in main
    assert "MOTION_RECOVERY_FRAMES" in main
    assert "MOTION_RECOVERY_MS := 300" in main
    assert "var motion_changed := live_motion_started_ms <= 0 or next_motion != previous_motion" in main
    assert 'live_debug_stats["motion_continuations"]' in main
    assert "live_motion_started_ms = live_recovery_until_ms" in main
    assert 'if motion_name == "walk":' in main
    assert "MOTION_SUSTAIN_LOOPS.has(motion_name)" in main


def test_adapter_prevents_overlap_duplicate_and_out_of_order_regressions() -> None:
    adapter = (REFERENCE / "scripts" / "frame_adapter.gd").read_text()
    assert "var _request_in_flight := false" in adapter
    assert '"phase": "skipped_in_flight"' in adapter
    assert "if tick <= current_tick:" in adapter
    assert '"duplicate" if tick == current_tick else "older"' in adapter
    assert "request_state.emit" in adapter
    assert "HTTPClient.METHOD_GET" in adapter
    assert "METHOD_POST" not in adapter
    assert "/api/step" not in adapter


def test_web_debug_surface_exposes_required_presentation_observability_without_world_writes() -> None:
    main = (REFERENCE / "scripts" / "main.gd").read_text()
    required = {
        "arrival_interval_ms",
        "selected_motion",
        "rendered_motion",
        "motion_started_ms",
        "motion_elapsed_ms",
        "transition_started_ms",
        "transition_elapsed_ms",
        "transition_duration_ms",
        "rendered_actor_position",
        "rendered_actor_anchor",
        "target_anchor",
        "animation_frame",
        "action_object_visible",
        "last_event_route",
        "window.__terrariumDebug",
    }
    for item in required:
        assert item in main
    assert "terrarium_debug=1" in main
    assert "terrarium_poll_ms" in main
    assert "/api/step" not in main
    assert "METHOD_POST" not in main


def test_web_delivery_hardening_disables_stale_asset_cache_and_preflights_port() -> None:
    gateway = (ROOT / "tools" / "godot_web_gateway.py").read_text()
    launcher = (ROOT / "scripts" / "run_godot_web_canary.sh").read_text()
    preset = (REFERENCE / "export_presets.cfg").read_text()
    main = (REFERENCE / "scripts" / "main.gd").read_text()
    assert 'cache_control="no-store"' in gateway
    assert 'sock.bind(("0.0.0.0", port))' in launcher
    assert "Terrarium Godot web presentation port {port} is already in use" in launcher
    assert "TERRARIUM_GODOT_WEB_PORT=<port>" in launcher
    assert "window.__terrariumBrowserErrors=[]" in preset
    assert "unhandledrejection" in preset
    assert "browser_errors:window.__terrariumBrowserErrors||[]" in main
