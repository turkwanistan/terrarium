# Terrarium — Godot full-room presentation candidate

**Status: adoption-ready, not cut over.** This project extends the approved pre-regression Reference-v2 visual direction into a full Terrarium presentation path without moving simulation authority into Godot. Canvas remains intact until an explicit cutover decision.

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

For the cutover-candidate path, prefer the presentation-only launcher after the canonical world is already running:

```bash
GODOT_BIN=/path/to/godot ./scripts/run_godot_live_candidate.sh
```

That launcher does **not** regenerate art, start/step/migrate the world, or perform a cutover. It discovers an existing read-only `/api/frame` endpoint (or accepts `TERRARIUM_API_URL`) and refuses accidental headless/llvmpipe launch unless explicitly overridden. Canvas remains the fallback until an explicit cutover decision.

The live runtime port is deployment-dependent; use the currently running Terrarium endpoint rather than assuming `8765`.

## Review and acceptance

- generated art review: `artifacts/godot-art-gate/reference-v3-review.html`
- acceptance record: `artifacts/godot-art-gate/reference-v3-adoption-gate.json`
- focused tests: `tests/test_godot_presentation.py`

The adoption gate requires actual Godot output, not only source PNG or HTML reconstruction. Native Godot 4.7.2 X11/OpenGL captures have validated the three environment variants, canonical route progression, bed choreography, carry/place, and representative non-thread object carry.
