# Terrarium — Godot full-room presentation candidate

**Status: browser-canary source ready; generated Web payload + extended live UAT pending.** Explicit cutover approval was received on 2026-08-29. Normal viewing is now targeted at a single-threaded Godot Web export served from the OptiPlex, so viewing PCs do not need Godot or a repository checkout. Native Godot remains an explicit validation/development client. Canvas remains intact as immediate same-world rollback until the browser canary passes.

## Locked art direction

- 400×240 authored logical surface; 800×480 exact nearest-neighbor presentation
- pragmatic overhead/three-quarter room projection; no isometric convergence
- warm timber + cream plaster + saturated blue + deep green material hierarchy
- selective chromatic outlines, compact contact shadows, shallow furniture top planes
- dense but curated lived-in prop detail
- compact side/three-quarter Moss from accepted `display/art/moss/` identity
- rejected frontal/chest-forward Moss experiment removed from generation

See repository-root `ART_DIRECTION.md` and `MOSS_SPEC.md`.

## Authored variants

`1` spring/day, `2` rain, `3` winter warm night. Live canonical night currently uses the approved warm-night treatment rather than falsely presenting night as daylight. Season-specific night variants remain optional future visual refinement.

## Production motions

Press `Space` to cycle:

`idle → walk → inspect → nudge → rest → loaf → groom → stretch → sleep → wake → pickup→carry → place → look/orient → window-watch`

Sleep/wake includes explicit floor-gate → mattress → supported-hold choreography and a sleep/wake-only bed-front occluder. Carry/place supports every canonical persistent object identity and its authored interaction states: blue stone, amber leaf, acorn, shell, red thread, and glass star.

Deterministic CLI capture supports `--variant`, `--motion`, `--manual-ms`, and `--capture`.

## Minimal live bridge

```bash
--live --api-url http://127.0.0.1:8080
```

The adapter polls canonical `GET /api/frame` every three seconds and is read-only. It consumes presentation-relevant canonical state only.

Presentation behavior includes:

- five explicit visual zone anchors aligned to the re-authored room composition;
- local canonical coordinate offsets preserved around those anchors;
- canonical `last_event.route` transformed into the visual layout and interpolated over 2.6 seconds;
- duplicate canonical ticks ignored so route transitions cannot restart from repeated polling;
- canonical activity/facing/object state selects authored Moss/object assets;
- no `POST`, no `/api/step`, no database access, no simulation planning, and no world-state writes.

Unknown future zones fail safely to the neutral 800×480 → 400×240 projection instead of inventing a destination.

## Run

From repository root:

```bash
GODOT_BIN=/path/to/godot ./scripts/run_godot_reference_v2.sh
```

Examples:

```bash
# deterministic authored review
GODOT_BIN=/path/to/godot ./scripts/run_godot_reference_v2.sh --variant rain --motion walk

# consume canonical Terrarium state in the development launcher
GODOT_BIN=/path/to/godot ./scripts/run_godot_reference_v2.sh --live --api-url http://127.0.0.1:8765
```

For normal canary presentation, keep the canonical world running separately and start the repository-root selector on the OptiPlex:

```bash
./scripts/run_presentation.sh
```

The selector starts the presentation-only HTTPS gateway and prints the browser URL. The viewing machine simply opens that URL; it does not need Godot, this repository, or WSL. The Web export automatically uses its serving origin for read-only frame polling.

Web export is defined by `export_presets.cfg` with thread/extension support disabled. `.github/workflows/build-godot-web.yml` produces the generated `display/web/godot/` payload from pinned Godot 4.7.2 release assets. Normal startup consumes that payload and never regenerates art or compiles Godot.

The gateway exposes only static Web assets plus `GET /api/frame` and `GET /api/health`; it rejects write methods and fails the entry page closed if canonical frame authority is unavailable. The canary uses local HTTPS because remote Godot Web delivery requires a secure browser context.

Native comparison/UAT remains available explicitly:

```bash
TERRARIUM_API_URL=http://host:port GODOT_BIN=/path/to/godot ./scripts/run_presentation.sh --native
```

Canvas rollback remains `./scripts/run_presentation.sh --canvas` (or the canonical world URL printed by `run_lan.sh`). The live runtime port is deployment-dependent; use the currently running Terrarium endpoint rather than assuming `8765`.

## Review and acceptance

- generated art review: `artifacts/godot-art-gate/reference-v3-review.html`
- acceptance record: `artifacts/godot-art-gate/reference-v3-adoption-gate.json`
- focused tests: `tests/test_godot_presentation.py`

The adoption gate requires actual Godot output, not only source PNG or HTML reconstruction. Native Godot 4.7.2 X11/OpenGL captures have validated the three environment variants, canonical route progression, bed choreography, carry/place, and representative non-thread object carry.
