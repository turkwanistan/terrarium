# Pixel-Art Overhaul — Iteration 8B: Room Recomposition

**Date:** 2026-08-27  
**Status:** ACCEPTED product checkpoint  
**Snapshot:** `20260828T023312695923Z-pixel-art-overhaul-iteration8b`  
**Seed/tick:** `1701 / 10080`  
**Semantic frame SHA256:** `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`  
**Renderer JS SHA256:** `e0ad1ddeeb85b0bf23aba987e88394d10f58a641e3da2e398730238f8bf52d10`  
**Authored-art tree SHA256:** `daaf4362afe7261e0bece29c7561aeb03333620bef5030898deeaec5d6f8ca96`

## Product weakness addressed

Iteration 8A removed the procedural-art architecture ceiling but intentionally left most of the habitat looking like the prior renderer. The remaining highest-value visual weakness was therefore composition itself: the room still depended on large room-specific JavaScript rectangle assemblies, subdued material separation, thin exterior treatment, and shallow zone identity.

Iteration 8B uses the accepted authored-art substrate to redraw the habitat as a coherent late-16-bit domestic diorama without changing Moss's simulation, semantic actions, navigation, events, habits, object state, or persistent-history authority.

## Authored room migration

The production habitat now routes its major visual masses through `display/art/`.

New authored assets include:

- `structure.room-shell` — full wall/floor/material shell, structural trim, sparse wall irregularity, floor seams and restrained grain;
- `environment.window-view` — cool exterior distance, layered foliage, branches and glass-light accents;
- `structure.window-alcove` — deeper frame, asymmetric curtains, sill and low perch;
- `structure.sleeping-nook` — stronger timber planes, layered bedding, asymmetry and domestic detail;
- `surface.living-rug` — broad quiet field with bounded woven motifs rather than uniform texture;
- `structure.activity-desk` — denser work/material cluster with papers, cloth, lamp-like/brass detail and stronger furniture planes;
- `prop.food-bowl` — authored companion to the existing water bowl;
- `front.collection-shelf-lips`, `front.activity-desk-lip`, and `front.window-perch` — real authored foreground occlusion pieces.

The existing collection shelf, water bowl, desk plant, floor-detail tile, and Moss idle asset remain part of the authored set. The manifest now contains **15 assets**.

Moss's remaining procedural action poses intentionally stay in place. Their migration is Iteration 8C, not hidden inside the room redraw.

## Palette/material redesign

`display/art/palettes/materials.json` now implements the richer saturated-natural target that 8A deliberately deferred.

The palette bank adds material roles for:

- deep/warm/gold timber;
- deep and bright foliage;
- blue/deep cloth;
- terracotta;
- flower accents;
- glass light;
- stone;
- brass.

All roles have deterministic dawn/day/dusk/night variants. The result keeps an earthy domestic base while strengthening chromatic darks, warm timber, natural greens, cool exterior values, cloth separation, and selective amber/terracotta focal color. It does not introduce neon color, gradients, bloom, or a giant universal master ramp.

## Zone identity and composition

The existing authoritative room zones and usable geometry were preserved while their visual identities became more distinct:

- **window:** the nature/weather/distance cluster now has exterior foliage, cooler distance color, deep casing and asymmetric cloth;
- **sleeping nook:** warmer timber, layered cloth and asymmetry make it read as softness/safety rather than a generic bed block;
- **rug/open space:** remains intentionally broad and comparatively quiet so Moss, carried objects and floor interactions stay readable;
- **collection shelf:** retains the strong authored memory/accumulation silhouette and now participates in true foreground occlusion through separate lip art;
- **activity corner:** has the highest controlled detail density through papers, plant, material contrast and authored desk construction.

The room is richer mainly at edges, furniture and focal clusters. Open movement space is not filled with decorative noise.

## Declarative depth integration

8B moves the room composition through the accepted scene-layer grammar rather than treating the entire room as one background function:

- `BACK` — authored room shell and window exterior/view;
- `STRUCTURE` — window alcove, sleeping nook, collection shelf, activity desk and plant;
- `SURFACE` — floor-detail tile, rug, authoritative path wear/history, and floor-located events such as sunlight;
- `WORLD` — bowls, persistent movable objects and located interior event presentation;
- `ACTORS` — Moss and carried-object acting;
- `FRONT` — shelf/desk lips, conditional window-perch occlusion, and sleep foreground causality.

During UAT, a final layer audit caught the floor-detail tile and bowls being drawn from broader neighboring passes despite correct manifest declarations. They were moved into `SURFACE` and `WORLD` respectively before acceptance. This is why 8B's layer contract is not only metadata; the production draw path now follows it for the recomposed room.

## Persistent history and event preservation

8B did not replace canonical aftermath with decorative storytelling.

The renderer still derives:

- path wear from authoritative habitat counters;
- sleeping-nook compression/creases from sleep history;
- activity-corner paper/clutter buildup from activity history;
- window smudges/wet marks from watch/weather history;
- sunlight, bird, rain, thunder, moth and leaf-contact presentation from authoritative world-event state;
- object placement from canonical object coordinates;
- Moss movement from continuous authoritative routes.

The 16×16 art grammar remains presentation-only. No canonical route, target, collision, object position, or event lifecycle was quantized to the art grid.

## Art-direction review

`tools/capture_art_direction_matrix.py` generated 8B-specific deterministic files:

- `artifacts/iteration8b-art-direction-fixtures.json`;
- `artifacts/iteration8b-art-direction-matrix.json`.

The matrix keeps the same **13 semantic scenarios** used for 8A so visual comparison remains controlled across dawn/day/dusk/night, clear/rain/mist, fresh/lived-in history, Moss poses/actions, and selected situational events. The manifest is pinned to the accepted renderer and authored-art hashes.

Subjective visual quality remains a direct browser/vision judgment. No numerical beauty/charm score was introduced.

## Browser / temporal UAT

UAT used isolated `/tmp/terrarium-iteration8b-uat` state and never canonical Moss.

Representative final production-browser states reached `Terrarium Temporal ready` with **zero console errors**. The harness repeatedly surfaced one non-fatal warning during some sequence/probe loads; it did not correspond to an art-load, renderer, fixture, or temporal failure.

Final raster evidence:

- dawn clear fresh idle: `fnv1a32:674275bd`;
- day clear fresh idle: `fnv1a32:29e7d52d`;
- day clear lived idle: `fnv1a32:32bda785`;
- dusk mist fresh idle: `fnv1a32:4ce58c6d`;
- night rain lived idle: `fnv1a32:f98a9bf5`.

Every sampled raster preserved exact **400×240 → 800×480** 2× scaling with smoothing disabled and zero scale-error blocks. Repeating the day-clear fixture reproduced `fnv1a32:29e7d52d` exactly.

Temporal evidence remained healthy after the richer room composition:

- inspect: 11 samples / 7 distinct raster states;
- sleep transition: 11 / 9;
- moth engagement: 11 / 8;
- continuity probe: **0 px** rebase jump;
- real RAF probe: **110 frames / 1816.6 ms**, p50 **16.7 ms**, p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms.

The promoted `grid-quantized-temporal-render-auditor-r1` capability remains unavailable for direct invocation through the frozen current MCP/Lab surface. No imitation auditor was created. Its applicable objective rejection classes were exercised through the existing deterministic temporal/raster/continuity/RAF path.

## Simulation preservation

There is no diff from accepted 8A in:

- `terrarium/engine.py`;
- `terrarium/models.py`;
- `terrarium/frame.py`;
- `terrarium/spatial.py`;
- `terrarium/events.py`;
- `terrarium/store.py`;
- `terrarium/replay.py`.

The 8B seed-1701/tick-10080 semantic frame SHA256 is:

`e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`

That is identical to accepted Iterations 7 and 8A at the same seed/tick. The room changed visually; Moss's world did not change semantically.

## Validation

- pytest: **46/46 PASS**;
- Python-3.10 grammar guard: **35 Python sources PASS**;
- JavaScript syntax: **PASS**;
- authored manifest/palette/asset schema and bounds validation: **PASS**;
- no `Math.random`, gradients, `ctx.ellipse`, or `roundRect` in the renderer: **PASS**;
- technical evaluator / append-only event chain / restart / exact replay: **PASS**;
- behavior, seeds 1701/1702/42/999 over 10,080 steps: **all PASS**;
- spatial, same four seeds / 10,080 steps: **all PASS**;
- coherence, same four seeds / 10,080 steps: **all PASS**;
- habits, same four seeds / 10,080 steps: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8B regression matrix: **PASS**.

Primary evidence:

- `artifacts/pixel-art-overhaul-iteration8b.json`;
- `artifacts/pixel-art-overhaul-iteration8b-regression-matrix.json`;
- `artifacts/pixel-art-overhaul-iteration8b-browser-uat.json`;
- `artifacts/pixel-art-overhaul-iteration8b-technical.json`;
- `artifacts/pixel-art-overhaul-iteration8b-repertoire.json`;
- `artifacts/pixel-art-overhaul-iteration8b-situations.json`;
- `artifacts/iteration8b-art-direction-matrix.json`;
- `artifacts/iteration8b-art-direction-fixtures.json`;
- per-seed behavior/spatial/coherence/habit artifacts under `artifacts/pixel-art-overhaul-iteration8b-*`;
- browser evidence under `artifacts/iteration8b-browser-evidence/`.

## SBC / Gen18 decision

**NO Gen18.** The work exposed no reusable platform deficiency. The needed changes were Terrarium-specific art assets, palette/material tuning, scene composition, and renderer wiring. Existing project execution, deterministic fixtures, browser access, replay/snapshot infrastructure, and evaluation tooling were sufficient.

Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

## Next product iteration

**Iteration 8C — Moss Sprite Overhaul.**

Use the accepted authored-art pipeline to replace Moss's remaining procedural action/body-part assembly with deliberate low-frame authored sprites while preserving the current semantic action vocabulary, timing authority, target/contact rules, possession continuity, and navigation. The room is now visually mature enough that Moss is the obvious next visual bottleneck.
