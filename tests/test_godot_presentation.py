from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "display" / "godot"


def _png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    return struct.unpack(">II", raw[16:24])


def test_godot_project_preserves_pixel_contract():
    text = (GODOT / "project.godot").read_text()
    assert "size/viewport_width=400" in text
    assert "size/viewport_height=240" in text
    assert "size/window_width_override=800" in text
    assert "size/window_height_override=480" in text
    assert 'stretch/scale_mode="integer"' in text
    assert "default_texture_filter=0" in text
    assert "snap_2d_transforms_to_pixel=true" in text


def test_vertical_slice_has_conventional_raster_art_and_density():
    manifest = json.loads((GODOT / "art" / "slice_manifest.json").read_text())
    assert manifest["schema"] == "terrarium.godot-slice-manifest.v1"
    assert manifest["art_surface"] == [400, 240]
    assert manifest["semantic_frame"] == [800, 480]
    assert manifest["authored_detail_instances"] >= 20
    assert _png_size(GODOT / "art" / "room_back.png") == (400, 240)
    assert _png_size(GODOT / "art" / "window_spring.png") == (148, 148)
    assert _png_size(GODOT / "art" / "moss_idle.png") == (46, 36)
    assert _png_size(GODOT / "art" / "object_red_thread_nested.png") == (16, 16)
    assert any(entry["layer"] == "Foreground" for entry in manifest["static"])
    assert len(manifest["y_sorted"]) >= 10


def test_portable_animation_vocabulary_has_four_frame_walk():
    source = json.loads((ROOT / "presentation" / "animations" / "moss.json").read_text())
    mirror = json.loads((GODOT / "art" / "moss_animations.json").read_text())
    assert source == mirror
    assert source["schema"] == "terrarium.presentation-animation.v1"
    walk = source["animations"]["walk"]
    assert len(walk["frames"]) == 4
    assert walk["durations_ms"] == [180, 180, 180, 180]
    assert all("res://" not in frame for anim in source["animations"].values() for frame in anim["frames"])


def test_fixture_pack_is_real_frame_v1_and_deterministic(tmp_path):
    one = tmp_path / "one.json"
    two = tmp_path / "two.json"
    tool = ROOT / "tools" / "build_godot_vertical_slice_fixtures.py"
    for out in (one, two):
        result = subprocess.run([sys.executable, str(tool), "--output", str(out)], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
    assert hashlib.sha256(one.read_bytes()).digest() == hashlib.sha256(two.read_bytes()).digest()
    pack = json.loads(one.read_text())
    assert pack["schema"] == "terrarium.godot-fixtures.v1"
    required = {
        "spring_clear_idle", "spring_rain_idle", "winter_warm_night", "walk_to_window",
        "inspect_red_thread", "pickup_red_thread", "carry_walk", "red_thread_rumpled", "red_thread_nested",
    }
    assert required <= set(pack["scenarios"])
    for scenario in pack["scenarios"].values():
        for frame in (scenario["source"], scenario["target"]):
            assert frame["schema"] == "terrarium.frame.v1"
            assert (frame["logical_width"], frame["logical_height"]) == (800, 480)
    assert pack["scenarios"]["spring_rain_idle"]["target"]["weather"] == "rain"
    winter = pack["scenarios"]["winter_warm_night"]["target"]
    assert winter["lighting"] == "night"
    assert winter["season"]["name"] == "winter"
    assert pack["scenarios"]["red_thread_rumpled"]["target"]["last_event"]["object_state_after"] == "rumpled"
    assert pack["scenarios"]["red_thread_nested"]["target"]["last_event"]["object_state_after"] == "nested"


def test_frame_adapter_is_read_only_and_explicit():
    text = (GODOT / "scripts" / "frame_adapter.gd").read_text()
    assert 'const FRAME_SCHEMA := "terrarium.frame.v1"' in text
    assert '"/api/frame"' in text
    assert "HTTPClient.METHOD_GET" in text
    assert "METHOD_POST" not in text
    assert "/api/step" not in text
    assert "SQLite" not in text


def test_canvas_renderer_remains_present_and_unchanged_from_iteration9():
    path = ROOT / "display" / "web" / "app.js"
    assert path.is_file()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5"

REFERENCE_V3 = ROOT / "display" / "godot_reference_v2"


def test_reference_v3_locks_palette_only_authored_moss_and_full_motion_set():
    generator = (REFERENCE_V3 / "tools" / "generate_reference_v2.py").read_text()
    assert "def moss_reference_idle" not in generator
    manifest = json.loads((REFERENCE_V3 / "art" / "hero_manifest.json").read_text())
    assert manifest["schema"] == "terrarium.reference-godot-poc-v3"
    assert "exact authored Moss geometry" in manifest["visual_baseline"]
    assert "palette mapping only" in manifest["visual_baseline"]
    assert set(manifest["motions"]) == {
        "idle", "walk", "inspect", "nudge", "rest", "loaf", "groom", "stretch",
        "sleep", "wake", "carry", "place", "look", "window_watch"
    }
    required = {
        "moss_idle_0.png", "moss_walk_3.png", "moss_inspect_3.png", "moss_nudge_4.png",
        "moss_rest_0.png", "moss_loaf_0.png", "moss_groom_3.png", "moss_stretch_3.png",
        "moss_sleep_4.png", "moss_wake_3.png", "moss_carry_4.png", "moss_place_4.png",
        "moss_look_1.png", "moss_window_watch_1.png",
    }
    assert required <= {p.name for p in (REFERENCE_V3 / "art").glob("moss_*.png")}
    assert all(_png_size(REFERENCE_V3 / "art" / name) == (60, 52) for name in required)
    assert _png_size(REFERENCE_V3 / "art" / "bed_front_lip.png") == (400, 240)
    main = (REFERENCE_V3 / "scripts" / "main.gd").read_text()
    assert "bed_occluder.visible = motion in [\"sleep\", \"wake\"]" in main


def test_reference_v3_production_moss_is_exact_authored_geometry_plus_palette(tmp_path):
    import importlib.util

    tool = REFERENCE_V3 / "tools" / "generate_reference_v2.py"
    spec = importlib.util.spec_from_file_location("terrarium_reference_v3_generator", tool)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    production = {
        "idle": ("idle",),
        "walk": tuple(f"walk-{i}" for i in range(4)),
        "inspect": ("inspect-anticipate", "inspect-contact", "inspect-hold", "inspect-recover"),
        "nudge": ("nudge-anticipate", "nudge-contact", "nudge-press", "nudge-hold", "nudge-recover"),
        "rest": ("rest",),
        "loaf": ("loaf",),
        "groom": ("groom-start", "groom-contact", "groom-hold", "groom-recover"),
        "stretch": ("stretch-ready", "stretch-extend", "stretch-hold", "stretch-recover"),
        "sleep": ("sleep-settle0", "sleep-settle1", "sleep-settle2", "sleep-settle3", "sleep-curled"),
        "wake": tuple(f"wake-{i}" for i in range(4)),
        "carry": ("pickup-anticipate", "pickup-contact", "pickup-lift", "pickup-hold", "carry"),
        "place": ("place-lower", "place-contact", "place-hold", "place-release", "place-recover"),
        "look": ("react", "idle"),
        "window_watch": ("window-ready", "window-watch"),
    }

    for motion, assets in production.items():
        for index, asset in enumerate(assets):
            expected = tmp_path / f"{motion}-{index}.png"
            module.moss_source_palette(asset).save(expected)
            actual = REFERENCE_V3 / "art" / f"moss_{motion}_{index}.png"
            assert actual.read_bytes() == expected.read_bytes(), (motion, index, asset)

    # Legacy deterministic idle aliases must remain the exact chosen authored/palette-only idle.
    idle = (REFERENCE_V3 / "art" / "moss_idle_0.png").read_bytes()
    assert idle == (REFERENCE_V3 / "art" / "review" / "moss_idle_source_palette.png").read_bytes()
    assert all((REFERENCE_V3 / "art" / f"moss_idle_{i}.png").read_bytes() == idle for i in range(1, 4))


def test_reference_v3_maps_full_canonical_activity_repertoire_and_preserves_motion_clock():
    main = (REFERENCE_V3 / "scripts" / "main.gd").read_text()
    for activity, motion in {
        "idle":"idle", "rest":"rest", "walk":"walk", "explore":"walk",
        "inspect":"inspect", "nudge":"nudge", "carry":"carry", "place":"place",
        "loaf":"loaf", "groom":"groom", "stretch":"stretch", "react":"look",
        "look_outside":"window_watch", "sleep":"sleep", "wake":"wake",
    }.items():
        assert f'"{activity}": "{motion}"' in main
    assert '"pickup"' not in main.split("const CANONICAL_ACTIVITY_TO_MOTION :=", 1)[1].split("}", 1)[0]
    assert "live_motion_started_ms" in main
    assert "if live_motion_started_ms <= 0 or next_motion != motion:" in main
    assert "motion_elapsed_ms" in main


def test_reference_v3_covers_all_canonical_persistent_object_states():
    manifest = json.loads((REFERENCE_V3 / "art" / "hero_manifest.json").read_text())
    expected = {
        "blue_stone": ["settled", "rolled"],
        "amber_leaf": ["fresh", "handled"],
        "acorn": ["settled", "rolled"],
        "shell": ["handled", "displayed"],
        "red_thread": ["loose", "rumpled", "nested"],
        "glass_star": ["handled", "displayed"],
    }
    assert manifest["live_object_support"] == expected
    for object_id, states in expected.items():
        for state in states:
            path = REFERENCE_V3 / "art" / f"object_{object_id}_{state}.png"
            assert path.is_file()
            assert _png_size(path) == (16, 14)
    main = (REFERENCE_V3 / "scripts" / "main.gd").read_text()
    assert "LIVE_OBJECT_TEXTURES" in main
    assert "LIVE_OBJECT_DEFAULT_STATES" in main
    for object_id in expected:
        assert f'"{object_id}"' in main


def test_reference_v3_live_bridge_is_read_only_and_simulation_free():
    adapter = (REFERENCE_V3 / "scripts" / "frame_adapter.gd").read_text()
    main = (REFERENCE_V3 / "scripts" / "main.gd").read_text()
    assert '"/api/frame"' in adapter
    assert "HTTPClient.METHOD_GET" in adapter
    assert "METHOD_POST" not in adapter
    assert "/api/step" not in adapter
    assert "SQLite" not in adapter
    assert '"--live"' in main
    assert '"--api-url"' in main
    assert "0.5" in main  # semantic 800x480 -> 400x240 presentation transform


def test_reference_v3_generator_is_deterministic(tmp_path):
    tool = REFERENCE_V3 / "tools" / "generate_reference_v2.py"

    def tree_hash() -> str:
        digest = hashlib.sha256()
        for path in sorted((REFERENCE_V3 / "art").glob("*.png")):
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
        digest.update((REFERENCE_V3 / "art" / "hero_manifest.json").read_bytes())
        return digest.hexdigest()

    first = subprocess.run([sys.executable, str(tool)], cwd=ROOT, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    h1 = tree_hash()
    second = subprocess.run([sys.executable, str(tool)], cwd=ROOT, text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    assert tree_hash() == h1


def test_live_candidate_launcher_is_opt_in_read_only_and_cpu_guarded():
    launcher = (ROOT / "scripts" / "run_godot_live_candidate.sh").read_text()
    assert "--live --api-url" in launcher
    assert '"/api/frame"' in launcher or '/api/frame' in launcher
    assert "generate_reference_v2.py" not in launcher
    assert "terrarium.api.server" not in launcher
    assert "/api/step" not in launcher
    assert "METHOD_POST" not in launcher
    assert "TERRARIUM_GODOT_HEADLESS_OK" in launcher
    assert "TERRARIUM_GODOT_SOFTWARE_RENDER_OK" in launcher
    assert "llvmpipe" in launcher
    assert "Canvas remains available" in launcher


def test_presentation_selector_defaults_to_godot_web_and_keeps_explicit_rollbacks():
    selector = (ROOT / "scripts" / "run_presentation.sh").read_text()
    assert 'mode="web"' in selector
    assert "--godot|--web|--native|--canvas" in selector
    assert 'exec "$ROOT/scripts/run_godot_web_canary.sh"' in selector
    assert 'exec "$ROOT/scripts/run_godot_live_candidate.sh"' in selector
    assert 'canvas_url="$api_url/"' in selector
    assert '"/api/frame"' in selector or '/api/frame' in selector
    assert "terrarium.api.server" not in selector
    assert "/api/step" not in selector
    assert "generate_reference_v2.py" not in selector
    assert "TERRARIUM_CANVAS_PRINT_ONLY" in selector


def test_windows_presentation_selector_defaults_to_web_and_keeps_native_canvas_options():
    selector = (ROOT / "scripts" / "run_presentation.ps1").read_text()
    assert '[string]$Mode = "web"' in selector
    assert 'ValidateSet("web", "native", "canvas")' in selector
    assert "TERRARIUM_PRESENTATION_URL" in selector
    assert '"https://$($api.Host):$GatewayPort/"' in selector
    assert '"/api/frame"' in selector
    assert "Invoke-RestMethod" in selector
    assert "--live --api-url" in selector
    assert "terrarium.api.server" not in selector
    assert "/api/step" not in selector
    assert "generate_reference_v2.py" not in selector
    assert "Start-Process $GatewayUrl" in selector
    assert "Start-Process ($ApiUrl + \"/\")" in selector


def test_reference_v3_web_export_is_single_threaded_and_same_origin_live():
    preset = (REFERENCE_V3 / "export_presets.cfg").read_text()
    main = (REFERENCE_V3 / "scripts" / "main.gd").read_text()
    assert 'platform="Web"' in preset
    assert 'variant/thread_support=false' in preset
    assert 'variant/extensions_support=false' in preset
    assert 'progressive_web_app/enabled=false' in preset
    assert 'OS.has_feature("web")' in main
    assert 'live_mode = true' in main
    assert 'JavaScriptBridge.get_interface("window")' in main
    assert 'window.location.origin' in main
    assert 'api_url_explicit = true' in main


def test_godot_web_canary_launcher_is_presentation_only_and_https_guarded():
    launcher = (ROOT / "scripts" / "run_godot_web_canary.sh").read_text()
    gateway = (ROOT / "tools" / "godot_web_gateway.py").read_text()
    assert "display/web/godot" in launcher
    assert "openssl req -x509" in launcher
    assert "tools/godot_web_gateway.py" in launcher
    assert "terrarium.api.server" not in launcher
    assert "/api/step" not in launcher
    assert "--upstream" in launcher
    assert 'ALLOWED_API_PATHS = {"/api/frame", "/api/health"}' in gateway
    assert "ssl.PROTOCOL_TLS_SERVER" in gateway
    assert "do_POST" in gateway
    assert "HTTPStatus.METHOD_NOT_ALLOWED" in gateway
    assert "canonical Terrarium frame endpoint unavailable" in gateway
    assert "/api/step" not in gateway
    assert "WorldEngine" not in gateway
    assert "WorldStore" not in gateway


def test_godot_web_build_workflow_is_pinned_and_commits_only_generated_payload():
    workflow = (ROOT / ".github" / "workflows" / "build-godot-web.yml").read_text()
    assert 'GODOT_VERSION: "4.7.2"' in workflow
    assert 'GODOT_EDITOR_SHA256: "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4"' in workflow
    assert 'GODOT_TEMPLATES_SHA256: "f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011"' in workflow
    assert 'web_nothreads_release.zip' in workflow
    assert '--export-release "Web"' in workflow
    assert 'display/web/godot' in workflow
    assert 'git add display/web/godot' in workflow
    assert 'Build Godot web presentation [skip ci]' in workflow
