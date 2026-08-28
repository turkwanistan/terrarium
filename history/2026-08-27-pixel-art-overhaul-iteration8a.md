# Pixel-Art Overhaul — Iteration 8A: Visual Grammar and Asset Pipeline

**Date:** 2026-08-27  
**Status:** ACCEPTED product checkpoint  
**Snapshot:** `20260828T020631095429Z-pixel-art-overhaul-iteration8a`  
**Seed/tick:** `1701 / 10080`  
**Semantic frame SHA256:** `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`  
**Renderer JS SHA256:** `993718bd2a30ce6fe47ce980f12af2512832c5c6a7fb4b4189068bef9bcfdae7`  
**Authored-art tree SHA256:** `644d19610ac740d5867b36bd266fdb075b7b0548360d5ed39339651cec76faa4`

## Product weakness addressed

After Iteration 7, Terrarium's deterministic simulation, behavior, spatial staging, persistence, and event ecology were materially ahead of the renderer's capacity for authored visual craft. The 400×240 pixel-native contract was sound, but finished room art, props, palette definitions, and Moss poses still lived primarily as drawing primitives inside `display/web/app.js`.

Iteration 8A removes that architectural ceiling without pretending to complete the room redraw. It establishes a real editable pixel-art substrate while preserving the existing renderer during migration.

## Authored art source and grammar

Added `display/art/` as the editable source root with:

- `manifest.json` — `terrarium.art-manifest.v1`;
- `palettes/materials.json` — `terrarium.palette-bank.v1`;
- palette-addressed pixel assets using `terrarium.pixel-asset.v1`;
- source directories for tiles, props, Moss, and environment art.

The manifest formally pins the static-world composition grammar to **16×16 source pixels** on the **400×240** art surface, yielding an exact **25×15** grid. This is renderer/art metadata only. No movement, collision, route, object-position, frame, or spatial contract was quantized to tiles.

Assets are authored as bounded deterministic run clusters `[x, y, width, height, palette_role]`. Runtime validation rejects bad schemas, dimensions, anchors, out-of-bounds runs, undeclared palette roles, invalid layer names, or an art grid that does not exactly cover the 400×240 surface.

## Palette/material architecture

The existing dawn/day/dusk/night colors were moved out of JavaScript into a palette bank rather than redesigned during the foundation pass. The bank defines named material families for timber, vegetation, cloth, environment, and Moss, and the renderer resolves asset colors through palette roles.

This preserves current appearance while removing the assumption that finished art must depend on one hard-coded JavaScript palette object. The richer saturated-natural palette redesign remains deliberate Iteration-8B work.

## Runtime compilation and caching

The production browser now loads the art manifest and palette bank before any live, snapshot, or temporal render. Valid assets are compiled once into smoothing-disabled offscreen canvases and cached by `asset@palette`.

Text asset interpretation therefore does not happen repeatedly in the frame loop. Asset loading is deterministic, and no runtime `Math.random` was introduced.

`terrarium/api/server.py` exposes the project-owned authored source read-only under `/art/`; it does not change world authority or add a mutation API.

## Representative production migration

Enough existing visual content was moved through the new path to prove coexistence end-to-end without a one-shot renderer rewrite:

- a **16×16 floor material/detail tile**;
- the **collection shelf** structural/furniture asset;
- the **water bowl** prop;
- a representative **Moss idle** frame;
- the **desk plant** environmental element.

Other room art and Moss action poses intentionally remain on the legacy procedural path for now. That coexistence is part of the acceptance target: Iterations 8B and 8C can migrate the room and hero in bounded passes rather than requiring a flag-day rewrite.

## Declarative scene depth

The renderer now has the generalized scene-layer contract:

1. `BACK`
2. `STRUCTURE`
3. `SURFACE`
4. `WORLD`
5. `ACTORS`
6. `FRONT`
7. `ALWAYS_FRONT`

A stable scene queue sorts entries by declared layer, then compatible base Y, then insertion serial. Production rendering already uses the queue for room/background composition, Y-ordered world objects, Moss, and foreground/occlusion passes. Asset-manifest layer declarations are validated now so Iteration 8B can progressively move remaining static composition into the same model without creating more draw-last exceptions.

Renderer ordering remains presentation-only. No semantic spatial authority moved into JavaScript.

## Art-direction review harness

Added `tools/capture_art_direction_matrix.py` and deterministic outputs:

- `artifacts/iteration8a-art-direction-fixtures.json`;
- `artifacts/iteration8a-art-direction-matrix.json`.

The matrix contains **13 production-renderer scenarios** spanning:

- dawn/day/dusk/night;
- clear/rain/mist;
- fresh vs deterministic lived-in history;
- idle, walk, inspect, and sleep presentation;
- sunlight, bird, thunder, and moth situations.

Every capture is tied to the production renderer hash, authored-art tree hash, and target semantic-frame hash. The workflow deliberately provides no numeric beauty score. It protects reproducibility and comparison; composition, charm, silhouette, material richness, and taste remain human/vision judgments.

## Browser / temporal UAT

UAT used an isolated development world at `/tmp/terrarium-iteration8a-uat`, never canonical Moss.

The production browser reached `Terrarium Temporal ready` with zero observed console errors for representative authored and legacy-coexistence cases including:

- dawn clear fresh idle;
- day clear fresh idle;
- dusk mist fresh idle;
- night rain lived-in idle;
- object inspection;
- sleep transition;
- moth engagement.

All captured raster samples preserved exact **400×240 → 800×480** 2× scaling with smoothing disabled and zero scale-error blocks. The day-clear fixture reproduced the identical raster hash `fnv1a32:e987c4ed` on a repeat load.

Temporal checks remained healthy after asset preload/caching and scene-queue integration:

- sleep transition: 11 samples / 9 distinct raster states;
- moth engagement: 11 samples / 8 distinct raster states;
- continuity probe: **0 px** rebase jump;
- real RAF probe: **110 frames / 1816.5 ms**, p50 **16.7 ms**, p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms.

The previously promoted `grid-quantized-temporal-render-auditor-r1` binary is not directly exposed by the current frozen MCP/Lab surface. No replacement auditor was forged. Its applicable rejection classes were exercised through the existing deterministic temporal-fixture path, exact-2× raster telemetry, continuity probe, and real RAF probe.

## Simulation preservation

There is no diff in `terrarium/engine.py`, `models.py`, `frame.py`, `spatial.py`, `events.py`, `store.py`, or `replay.py`.

The Iteration-8A snapshot at seed/tick `1701 / 10080` has semantic frame SHA256:

`e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`

That is **identical to the accepted Iteration-7 semantic frame hash** at the same seed/tick. The visual substrate changed; the authoritative simulation did not.

## Validation

- pytest: **45/45 PASS**;
- Python-3.10 grammar guard: **35 Python sources PASS**;
- JavaScript syntax: **PASS**;
- authored manifest/palette/asset schema and bounds validation: **PASS**;
- technical evaluator / append-only chain / restart / exact replay: **PASS**;
- behavior, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- spatial, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- coherence, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- habits, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational-event regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8A regression matrix: **PASS**.

Primary evidence:

- `artifacts/pixel-art-overhaul-iteration8a.json`;
- `artifacts/pixel-art-overhaul-iteration8a-regression-matrix.json`;
- `artifacts/pixel-art-overhaul-iteration8a-browser-uat.json`;
- `artifacts/pixel-art-overhaul-iteration8a-technical.json`;
- `artifacts/pixel-art-overhaul-iteration8a-repertoire.json`;
- `artifacts/pixel-art-overhaul-iteration8a-situations.json`;
- `artifacts/iteration8a-art-direction-matrix.json`;
- `artifacts/iteration8a-art-direction-fixtures.json`;
- per-seed behavior/spatial/coherence/habit artifacts under `artifacts/pixel-art-overhaul-iteration8a-*`;
- browser evidence under `artifacts/iteration8a-browser-evidence/`.

## SBC / Gen18 decision

**NO Gen18.** The needed asset schema, palette bank, deterministic cache, scene queue, server art route, and review matrix are naturally Terrarium-local product infrastructure. Existing project execution, deterministic simulation, snapshot/replay, browser tooling, and temporal fixture substrate were sufficient. No independent reusable platform deficiency materially blocked correct implementation.

Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

## Next product iteration

**Iteration 8B — Room Recomposition.**

Use the authored substrate to redraw the habitat into the richer saturated, layered, asymmetrical, materially specific target language. Migrate the room progressively, strengthen silhouettes and material families, improve window/exterior richness and foreground depth, and preserve quiet rug/open-space readability plus all authoritative history marks.

Do not turn 8B into the Moss sprite overhaul; authored action-pose migration remains Iteration 8C.
