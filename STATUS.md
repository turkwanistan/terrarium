# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8C: Moss Sprite Overhaul**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration8c.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8c.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8c-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8c-browser-uat.json`
- art-direction matrix: `artifacts/iteration8c-art-direction-matrix.json`
- art-direction fixtures: `artifacts/iteration8c-art-direction-fixtures.json`
- accepted snapshot: `20260828T030258821895Z-pixel-art-overhaul-iteration8c`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `a0f49cd9f58e8962f609369b9c6e0032b65fcf5aa8fbad63d128889415ac220a`
- authored-art tree SHA256: `a7f940c4f4d2b38849c1c9f5b2a6b453a2d2453027924bc24282da6fd2285e87`
- authored assets: **60 total / 46 Moss**
- behavior rules: `terrarium-rules-v6-situational-attention`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- habits: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

The seed-1701/tick-10080 semantic frame hash is identical to accepted Iterations 7/8A/8B. Iteration 8C changes renderer/art only; authoritative simulation state and behavior did not change.

## What Iteration 8C changed

Moss now renders from **46 deterministic authored pixel assets** under `display/art/moss/` covering the accepted visual families: planted idle, four-frame locomotion, inspect, nudge, pickup, carry, place, loaf/rest, groom, stretch, react/orient, window watch, sleep transition/curled sleep, and wake/unfold.

`display/web/app.js` now primarily maps canonical pose/action progress to authored frames and mirrors/stages them. Procedural finished body/head/leg/tail construction was removed. The only bounded procedural Moss detail retained is exact target-dependent contact reach for interaction alignment; it derives from the canonical target and does not invent behavior or mutate state.

Stillness is valid: the old time-driven whole-sprite idle/sleep bob was removed. Walk weight shift is authored into four discrete sprites while continuous route interpolation, facing, target/contact authority, and movement timing remain unchanged. Carried-object attachment and canonical object transfer/release remain governed by existing state.

## Room and palette integration

The accepted 8B room, scene-layer grammar, palette bank, foreground occlusion, history overlays, and continuous spatial geometry remain intact. Moss uses the same dawn/day/dusk/night dog palette roles and remains in `ACTORS`, behind existing `FRONT` furniture/bedding lips where appropriate.

The art grid remains presentation grammar only: **400×240 source → exact 2× 800×480**, nearest-neighbor, smoothing off. Canonical positions, routes, targets, events, object state, and history remain continuous semantic state.

## Browser / temporal UAT

Production-browser UAT used isolated `/tmp/terrarium-iteration8c-uat`; canonical Moss was never reset, replaced, or used as a fixture. The expanded 8C art-direction pack covers **25 scenarios**, including both walk directions, all object interaction families, quiet actions, window/sleep/wake, environmental palettes/weather/history, and situational-event contexts.

Key final results:

- deterministic fresh-day repeat: `fnv1a32:3ea5ca55` reproduced exactly;
- left walk: **11 samples / 7 distinct rasters**; right walk: **11 / 7**;
- inspect: **11 / 5**; nudge: **11 / 6**; pickup: **11 / 4**; placement: **11 / 7**;
- loaf: **11 / 3**; groom: **11 / 4**; stretch: **11 / 6**; window: **11 / 5**;
- sleep transition: **11 / 8**; waking: **11 / 6**; wake exit: **11 / 6**;
- situational sunlight/bird/thunder/moth sequences remain coherent;
- every sampled raster had **0 scale-error blocks**;
- continuity probe: **0 px** jump;
- RAF probe: **110 frames / 1816.6 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms;
- zero browser console errors; one repeated benign warning was observed during some sequence loads.

## Validation

- pytest: **47/47 PASS**;
- Python-3.10 grammar guard: **35 sources PASS**;
- JavaScript syntax: **PASS**;
- authored manifest/palette/asset schema and bounds: **60/60 PASS**;
- technical evaluator / append-only chain / restart / exact replay: **PASS**;
- behavior, spatial, coherence, and habits: seeds **1701 / 1702 / 42 / 999**, 10,080 steps each: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8C regression matrix: **PASS**.

There is no diff from accepted 8B in `terrarium/engine.py`, `terrarium/models.py`, `terrarium/frame.py`, `terrarium/spatial.py`, `terrarium/events.py`, `terrarium/situations.py`, `terrarium/store.py`, or `terrarium/replay.py`.

## SBC conclusion

The existing Terrarium authored-art schema, renderer, deterministic fixture system, project execution, and browser/evaluation tooling were sufficient. No reusable SBC substrate deficiency was exposed. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

**Gen18: NO**

## Next: Iteration 8D — Object Identity and Stateful Affordances

Resume the behavior/state milestone now that both room and protagonist are authored:

- differentiate object classes by meaningful affordance subsets;
- add authoritative persistent object-state transitions that change later possibilities;
- pair those states with authored visual variants;
- preserve spatial/replay/migration/habit authority;
- evaluate object-class differentiation, state-transition validity, persistence, and absence of generic-object collapse.

Success means object identity changes both what Moss can do and what the viewer can see afterward.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
