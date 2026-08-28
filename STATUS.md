# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8A: Visual Grammar and Asset Pipeline**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration8a.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8a.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8a-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8a-browser-uat.json`
- art-direction matrix: `artifacts/iteration8a-art-direction-matrix.json`
- art-direction fixtures: `artifacts/iteration8a-art-direction-fixtures.json`
- accepted snapshot: `20260828T020631095429Z-pixel-art-overhaul-iteration8a`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `993718bd2a30ce6fe47ce980f12af2512832c5c6a7fb4b4189068bef9bcfdae7`
- authored-art tree SHA256: `644d19610ac740d5867b36bd266fdb075b7b0548360d5ed39339651cec76faa4`
- behavior rules: `terrarium-rules-v6-situational-attention`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- behavior context: `terrarium.behavior-context.v1`
- habits: `terrarium.habits.v1`
- affordance history: `terrarium.affordances.v1`
- spatial schema: `terrarium.spatial.v1`

The semantic frame hash is identical to accepted Iteration 7 at the same seed/tick. Iteration 8A changed the renderer/art substrate, not Moss's authoritative simulation.

## What Iteration 8A established

Terrarium now has a real authored-art source tree under `display/art/` rather than relying on `display/web/app.js` as the sole home of finished pixel clusters.

The foundation includes:

- `terrarium.art-manifest.v1` with an exact **400×240** art surface, **16×16** static composition unit, and **25×15** art grid;
- `terrarium.pixel-asset.v1` palette-addressed run-cluster assets with strict dimension/bounds/role validation;
- `terrarium.palette-bank.v1` with named material families and dawn/day/dusk/night palette variants;
- deterministic preload and compilation of authored assets into smoothing-disabled offscreen canvases;
- an `asset@palette` runtime cache so text assets are not reinterpreted every frame;
- a generalized scene queue with `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT / ALWAYS_FRONT` ordering and compatible Y/base ordering;
- read-only `/art/` serving from the project-owned source tree;
- production-renderer metadata exposing art-grid, scene-layer, and authored-asset contracts;
- a deterministic art-direction fixture/matrix workflow tied to renderer, authored-art, and target-frame hashes.

The art grid is presentation grammar only. Canonical coordinates, blockers, routes, object placement, behavior, and `terrarium.spatial.v1` remain continuous and authoritative.

## Representative migration

Iteration 8A deliberately did not redraw the whole habitat. It proved the architecture with a cross-section of real production content:

- one 16×16 floor material/detail tile;
- the collection shelf structure;
- one water-bowl prop;
- a Moss idle frame;
- the activity-corner desk plant.

These authored assets coexist with unmigrated legacy procedural art. That bounded transition path is intentional: **Iteration 8B** migrates/recomposes the room, and **Iteration 8C** completes the Moss sprite overhaul.

The existing color values were externalized rather than substantially redesigned. This keeps 8A focused on substrate correctness while ensuring the architecture can support richer material-specific ramps and later time/weather/season variants.

## Art-direction review / browser UAT

`tools/capture_art_direction_matrix.py` builds **13 deterministic production-renderer scenarios** covering dawn/day/dusk/night, clear/rain/mist, fresh vs lived-in history, idle/walk/inspect/sleep, and representative sunlight/bird/thunder/moth situations.

Real 800×480 browser UAT used an isolated `/tmp/terrarium-iteration8a-uat` world and reached `Terrarium Temporal ready` with zero observed console errors across representative authored and legacy-coexistence cases. Captured rasters preserved exact 400×240→800×480 2× scaling, smoothing disabled, and zero scale-error blocks.

Additional temporal evidence:

- deterministic fresh-day repeat: identical `fnv1a32:e987c4ed` raster hash;
- sleep transition: 11 samples / 9 distinct raster states;
- moth engagement: 11 samples / 8 distinct raster states;
- continuity probe: **0 px** jump;
- RAF probe: **110 frames / 1816.5 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms.

The promoted `grid-quantized-temporal-render-auditor-r1` binary is not directly exposed by the current frozen MCP/Lab tool surface. No substitute capability was created. Its relevant rejection classes were exercised through the existing deterministic temporal fixture/raster/continuity/RAF path.

Subjective art quality still has no machine beauty score. Iteration 8A accepts the production substrate; the major taste/composition redraw begins in 8B.

## Validation

- pytest: **45/45 PASS**;
- Python-3.10 grammar guard: **35 sources PASS**;
- JavaScript syntax: **PASS**;
- authored asset manifest/palette/schema validation: **PASS**;
- technical evaluator / append-only event chain / restart / exact replay: **PASS**;
- behavior, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- spatial, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- coherence, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- habits, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8A regression matrix: **PASS**.

No simulation-authority source file changed. Canonical Moss was not reset, replaced, migrated, or used as a development fixture.

## SBC conclusion

No reusable substrate deficiency was exposed. Authored art files, the palette bank, renderer cache, scene queue, static art route, and art-review matrix fit cleanly inside Terrarium. Existing project execution, deterministic replay/snapshot support, browser access, and temporal fixture infrastructure were sufficient.

Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18 decision: NO.**

## Next: Iteration 8B — Room Recomposition

Use the accepted authored-art substrate to make the habitat itself inhabit the target visual territory:

- migrate/recompose the full room through authored assets;
- introduce the richer saturated-natural palette/material treatment;
- strengthen zone/furniture silhouettes and material specificity;
- increase controlled asymmetry and authored foliage/exterior richness;
- deepen foreground occlusion and framing;
- preserve the broad rug/open-space visual rest area;
- preserve all authoritative history marks and spatial validity.

Success for 8B is a still frame with Moss hidden that already reads as a deliberate, richly authored late-16-bit life-RPG interior. Moss's full authored action-sprite migration remains **Iteration 8C**.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Any host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
