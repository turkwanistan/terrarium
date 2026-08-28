from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "display" / "art"
LAYERS = {"BACK", "STRUCTURE", "SURFACE", "WORLD", "ACTORS", "FRONT", "ALWAYS_FRONT"}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_authored_art_manifest_grid_palette_and_cross_section_are_valid():
    manifest = _read(ART / "manifest.json")
    assert manifest["schema"] == "terrarium.art-manifest.v1"
    assert manifest["art_surface"] == [400, 240]
    assert manifest["tile_size"] == 16
    assert manifest["grid"] == [25, 15]
    assert manifest["grid"][0] * manifest["tile_size"] == manifest["art_surface"][0]
    assert manifest["grid"][1] * manifest["tile_size"] == manifest["art_surface"][1]

    palette_bank = _read(ART / manifest["palette_source"])
    assert palette_bank["schema"] == "terrarium.palette-bank.v1"
    roles = set(palette_bank["required_roles"])
    assert {"day", "dawn", "dusk", "night"} <= set(palette_bank["palettes"])
    assert {"timber", "vegetation", "cloth", "environment", "dog"} <= set(palette_bank["material_families"])
    for palette in palette_bank["palettes"].values():
        assert roles <= set(palette)
        assert all(isinstance(palette[role], str) and palette[role].startswith("#") for role in roles)

    kinds = set()
    ids = set()
    for entry in manifest["assets"]:
        assert entry["id"] not in ids
        ids.add(entry["id"])
        kinds.add(entry["kind"])
        assert entry["layer"] in LAYERS
        asset = _read(ART / entry["path"])
        assert asset["schema"] == "terrarium.pixel-asset.v1"
        assert asset["id"] == entry["id"]
        assert isinstance(asset["width"], int) and asset["width"] > 0
        assert isinstance(asset["height"], int) and asset["height"] > 0
        assert len(asset["anchor"]) == 2 and all(isinstance(v, int) for v in asset["anchor"])
        assert asset["runs"]
        for x, y, width, height, role in asset["runs"]:
            assert all(isinstance(v, int) for v in (x, y, width, height))
            assert x >= 0 and y >= 0 and width > 0 and height > 0
            assert x + width <= asset["width"] and y + height <= asset["height"]
            assert role in roles

    assert {"tile", "structure", "prop", "moss", "environment"} <= kinds


def test_renderer_uses_authored_art_cache_and_declarative_scene_layers():
    js = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    server = (ROOT / "terrarium" / "api" / "server.py").read_text(encoding="utf-8")
    assert "const SCENE_LAYERS" in js
    assert "const ART_CACHE = new Map()" in js
    assert "async function loadArtBundle" in js
    assert "function drawAuthoredAsset" in js
    assert "function createSceneQueue" in js
    assert "'/art/manifest.json'" in js
    assert "Math.random" not in js
    assert 'ART_ROOT = PROJECT_ROOT / "display" / "art"' in server
    assert 'parsed.path.startswith("/art/")' in server


def test_iteration8b_room_recomposition_is_authored_and_layered():
    manifest = _read(ART / "manifest.json")
    entries = {entry["id"]: entry for entry in manifest["assets"]}
    required = {
        "structure.room-shell": "BACK",
        "environment.window-view": "BACK",
        "structure.window-alcove": "STRUCTURE",
        "structure.sleeping-nook": "STRUCTURE",
        "surface.living-rug": "SURFACE",
        "structure.collection-shelf": "STRUCTURE",
        "structure.activity-desk": "STRUCTURE",
        "prop.water-bowl": "WORLD",
        "prop.food-bowl": "WORLD",
        "front.collection-shelf-lips": "FRONT",
        "front.activity-desk-lip": "FRONT",
        "front.window-perch": "FRONT",
    }
    for asset_id, layer in required.items():
        assert entries[asset_id]["layer"] == layer

    palette_bank = _read(ART / manifest["palette_source"])
    assert {"woodDeep", "woodWarm", "woodGold", "leafDeep", "leafBright", "clothBlue", "clothDeep", "terracotta", "glassLight", "brass"} <= set(palette_bank["required_roles"])

    js = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    assert "function drawWindowBack" in js
    assert "function drawWindowStructure" in js
    assert "function drawStructureLayer" in js
    assert "function drawSurfaceLayer" in js
    assert "function drawWorldAtmosphere" in js
    for asset_id in required:
        assert asset_id in js
    assert "room-shell-and-window-view" in js
    assert "room-zones" in js
    assert "room-surface-and-history" in js
    assert "world-atmosphere" in js


def test_iteration8c_moss_action_vocabulary_is_authored_not_body_part_assembled():
    manifest = _read(ART / "manifest.json")
    entries = {entry["id"]: entry for entry in manifest["assets"]}
    required = {
        "moss.idle",
        "moss.walk.0", "moss.walk.1", "moss.walk.2", "moss.walk.3",
        "moss.inspect.anticipate", "moss.inspect.contact", "moss.inspect.hold", "moss.inspect.recover",
        "moss.nudge.anticipate", "moss.nudge.contact", "moss.nudge.press", "moss.nudge.recover",
        "moss.pickup.anticipate", "moss.pickup.contact", "moss.pickup.lift", "moss.pickup.hold",
        "moss.carry",
        "moss.place.hold", "moss.place.lower", "moss.place.contact", "moss.place.release", "moss.place.recover",
        "moss.loaf", "moss.groom.start", "moss.groom.contact", "moss.groom.hold",
        "moss.stretch.ready", "moss.stretch.extend", "moss.stretch.hold",
        "moss.react", "moss.window.watch",
        "moss.sleep.settle0", "moss.sleep.settle1", "moss.sleep.settle2", "moss.sleep.settle3", "moss.sleep.curled",
        "moss.wake.0", "moss.wake.1", "moss.wake.2", "moss.wake.3",
    }
    assert required <= set(entries)
    moss_entries = [entry for entry in manifest["assets"] if entry["kind"] == "moss"]
    assert len(moss_entries) >= 40
    for entry in moss_entries:
        assert entry["layer"] == "ACTORS"
        asset = _read(ART / entry["path"])
        assert asset.get("meta", {}).get("action")
        assert asset.get("meta", {}).get("mirroring") == "horizontal"

    js = (ROOT / "display" / "web" / "app.js").read_text(encoding="utf-8")
    assert "function mossFrameAsset" in js
    assert "drawAuthoredAsset(assetId,x,baseY,paletteName" in js
    assert "function drawMossContactReach" in js
    assert "function body(" not in js
    assert "function head(" not in js
    assert "function plantedLegs(" not in js
    assert "function walkLegs(" not in js
    assert "function tail(" not in js
    assert "quiet-breathing" not in js
    assert "breathStep" not in js
