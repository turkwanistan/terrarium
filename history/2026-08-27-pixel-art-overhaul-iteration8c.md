# Pixel-Art Overhaul — Iteration 8C: Moss Sprite Overhaul

**Date:** 2026-08-27  
**Status:** ACCEPTED product checkpoint  
**Snapshot:** `20260828T030258821895Z-pixel-art-overhaul-iteration8c`  
**Seed/tick:** `1701 / 10080`  
**Semantic frame SHA256:** `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`  
**Renderer JS SHA256:** `a0f49cd9f58e8962f609369b9c6e0032b65fcf5aa8fbad63d128889415ac220a`  
**Authored-art tree SHA256:** `a7f940c4f4d2b38849c1c9f5b2a6b453a2d2453027924bc24282da6fd2285e87`

## Product weakness addressed

Iteration 8B brought the room up to the authored-art target while intentionally leaving Moss's finished action poses largely assembled at runtime from procedural body/head/leg/tail rectangles. That made the protagonist the clearest remaining visual bottleneck: the habitat looked deliberately illustrated while Moss still looked like renderer geometry.

Iteration 8C moves the accepted hero vocabulary into the same deterministic authored-art substrate without changing behavior, targets, movement, events, habits, object state, pacing, or world authority.

## Authored Moss vocabulary

The production manifest now contains **60 authored assets**, of which **46 are Moss sprites** under `display/art/moss/`.

The authored vocabulary covers:

- planted idle;
- four-frame left/right-mirrored locomotion;
- inspect anticipation/contact/hold/recovery;
- nudge anticipation/contact/press/hold/recovery;
- pickup anticipation/contact/lift/hold;
- stable carry;
- place hold/lower/contact/release/recovery;
- loaf/rest;
- groom start/contact/hold/recovery;
- stretch ready/extend/hold/recovery;
- react/orient;
- window ready/watch;
- sleep settle frames into curled sleep;
- wake/unfold back to standing.

The existing `terrarium.pixel-asset.v1` schema was sufficient. Assets remain text-addressable, palette-addressed, deterministic, diffable, bounds-validated, and compiled through the accepted offscreen cache. No sprite atlas service, external art runtime, or platform-level schema was required.

## Renderer migration

`display/web/app.js` no longer constructs Moss's finished body, head, ears, tail, or legs from helper rectangles. The renderer now:

1. reads the authoritative creature/activity state;
2. computes the same existing movement and activity progress;
3. maps that canonical state to a discrete authored Moss asset;
4. mirrors the authored asset when appropriate;
5. stages the asset at the authoritative continuous semantic position;
6. renders carried objects through the existing canonical attachment path.

A single bounded presentation exception remains: exact target-dependent forepaw reach during inspect/nudge/pickup/place. That small overlay derives from the canonical target/contact point and exists only to preserve precise variable contact alignment. It does not reconstruct Moss's finished silhouette, invent a target, move an object, mutate state, or create hidden behavior.

The previous time-driven whole-sprite idle/sleep bob was removed. Stillness is therefore a valid final hold. Visible locomotion weight shift comes from the authored four-frame walk vocabulary while route interpolation remains continuous and unchanged.

## Action and contact causality

Object presentation continues to respect canonical causality:

- approach and facing derive from authoritative route/target state;
- contact poses occur against the canonical target;
- pickup attachment still follows existing transfer progress;
- a carried object's world position stays coupled to Moss across locomotion/facing changes;
- placement uses the existing canonical placement state and release timing;
- the renderer does not visually invent object transfer before state/contact supports it.

The authored poses make anticipation, contact, hold, and recovery more visually distinct without adding new semantic action enums.

## Quiet acting and sleep

Loaf, groom, stretch, window watch, sleep, and wake now have distinct authored silhouettes rather than procedural deformation plus fidget. Sleep progresses through authored compression/settling frames into a static curled pose. Existing foreground bedding causality remains in `FRONT`, so Moss still settles physically into the accepted sleeping nook rather than drawing above it.

## Room and palette integration

Iteration 8C does not redesign the accepted 8B habitat. Moss remains in the existing `ACTORS` layer and continues to respect shelf/desk/window/bed foreground occlusion.

The sprites use the accepted palette bank's `dog`, `dogDark`, `dogLight`, `dogCream`, `eye`, and `shadow` roles across dawn/day/dusk/night variants. No unrelated character palette was introduced.

Visible non-shadow Moss bounds vary by pose from roughly **35–50 source pixels wide** and **21–38 source pixels tall**; active poses stay in the established hero scale while stretch deliberately extends the silhouette.

## Art-direction review

`tools/capture_art_direction_matrix.py` now builds an expanded 8C review pack with **25 semantic scenarios**. Coverage includes:

- dawn/day/dusk/night and clear/rain/mist context;
- fresh and lived-in history;
- left/right walk and carried walk;
- inspect, nudge, pickup, and placement;
- loaf, groom, stretch, reaction, and window watching;
- sleep transition, waking, and wake exit;
- sunlight, bird, thunder, and moth situational contexts.

Subjective production-renderer review accepted the protagonist migration: the major action silhouettes are authored, quiet poses are meaningfully distinct without fidget noise, sleep reads as supported, and Moss remains legible within the 8B room across environmental contexts. No numerical charm/beauty score was introduced.

## Browser / temporal UAT

UAT used isolated `/tmp/terrarium-iteration8c-uat` state and never canonical Moss.

All reviewed production-browser pages reached `Terrarium Temporal ready`. Zero console errors were observed; the browser harness surfaced the same benign warning seen in prior accepted temporal sequence loads.

Every sampled raster preserved exact **400×240 → 800×480** 2× nearest-neighbor scaling with smoothing disabled and **0 scale-error blocks**.

Representative static hashes:

- dawn clear fresh idle: `fnv1a32:a12957cd`;
- day clear fresh idle: `fnv1a32:3ea5ca55`;
- day clear lived idle: `fnv1a32:beb0276d`;
- dusk mist fresh idle: `fnv1a32:9e94a1cd`;
- night rain fresh idle: `fnv1a32:926fa625`;
- night rain lived idle: `fnv1a32:1a7a813d`.

Repeating the day-clear fixture reproduced `fnv1a32:3ea5ca55` exactly.

Representative temporal diversity:

- left walk: 11 samples / 7 distinct rasters;
- right walk: 11 / 7;
- inspect: 11 / 5;
- nudge: 11 / 6;
- pickup: 11 / 4;
- carried walk: 11 / 7;
- placement: 11 / 7;
- loaf: 11 / 3;
- groom: 11 / 4;
- stretch: 11 / 6;
- window transition: 11 / 5;
- sleep transition: 11 / 8;
- waking: 11 / 6;
- wake exit: 11 / 6;
- sunlight: 11 / 7;
- bird: 11 / 7;
- thunder: 11 / 10;
- moth: 11 / 6.

Continuity and pacing remained healthy:

- continuity probe: **0 px** rebase jump;
- real RAF probe: **110 frames / 1816.6 ms**;
- p50/p95: **16.7 ms**;
- max: **16.8 ms**;
- intervals above 34 ms: **0**;
- intervals above 50 ms: **0**.

## Simulation preservation

There is no diff from accepted 8B in:

- `terrarium/engine.py`;
- `terrarium/models.py`;
- `terrarium/frame.py`;
- `terrarium/spatial.py`;
- `terrarium/events.py`;
- `terrarium/situations.py`;
- `terrarium/store.py`;
- `terrarium/replay.py`.

The seed-1701/tick-10080 semantic frame SHA256 is:

`e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`

That is identical to accepted Iterations 7, 8A, and 8B. The protagonist changed visually; Moss's authoritative world did not change semantically.

## Validation

- pytest: **47/47 PASS**;
- Python-3.10 grammar guard: **35 Python sources PASS**;
- JavaScript syntax: **PASS**;
- authored manifest/palette/asset schema and bounds validation: **60/60 assets PASS**, including **46 Moss assets**;
- technical evaluator / append-only event chain / restart / exact replay: **PASS**;
- behavior, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- spatial, same four seeds / 10,080 steps: **all PASS**;
- coherence, same four seeds / 10,080 steps: **all PASS**;
- habits, same four seeds / 10,080 steps: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8C regression matrix: **PASS**.

Primary evidence:

- `artifacts/pixel-art-overhaul-iteration8c.json`;
- `artifacts/pixel-art-overhaul-iteration8c-regression-matrix.json`;
- `artifacts/pixel-art-overhaul-iteration8c-browser-uat.json`;
- `artifacts/pixel-art-overhaul-iteration8c-technical.json`;
- `artifacts/pixel-art-overhaul-iteration8c-repertoire.json`;
- `artifacts/pixel-art-overhaul-iteration8c-situations.json`;
- per-seed behavior/spatial/coherence/habit artifacts under `artifacts/pixel-art-overhaul-iteration8c-*`;
- `artifacts/iteration8c-art-direction-matrix.json`;
- `artifacts/iteration8c-art-direction-fixtures.json`;
- raw browser evidence under `artifacts/iteration8c-browser-evidence/`.

## SBC / Gen18 decision

**Gen18: NO.**

Iteration 8C exposed no reusable SBC substrate deficiency. The accepted Terrarium pixel-asset schema, renderer, deterministic fixture pack, project execution, browser UAT, replay/snapshot system, and evaluation tooling were sufficient. Additional sprite assets and project-local frame metadata are product work, not platform evidence.

Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

## Next product iteration

**Iteration 8D — Object Identity and Stateful Affordances.**

With both the habitat and protagonist now authored, resume the postponed behavior/state milestone: give small object archetypes meaningfully different affordance subsets and persistent canonical state transitions, then pair those states with authored visual variants so object identity changes both what Moss can do and what the viewer can see afterward.
