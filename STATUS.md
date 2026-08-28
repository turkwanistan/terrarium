# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8B: Room Recomposition**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration8b.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8b.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8b-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8b-browser-uat.json`
- art-direction matrix: `artifacts/iteration8b-art-direction-matrix.json`
- art-direction fixtures: `artifacts/iteration8b-art-direction-fixtures.json`
- accepted snapshot: `20260828T023312695923Z-pixel-art-overhaul-iteration8b`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `e0ad1ddeeb85b0bf23aba987e88394d10f58a641e3da2e398730238f8bf52d10`
- authored-art tree SHA256: `daaf4362afe7261e0bece29c7561aeb03333620bef5030898deeaec5d6f8ca96`
- authored asset count: **15**
- behavior rules: `terrarium-rules-v6-situational-attention`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- habits: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

The seed-1701/tick-10080 semantic frame hash is identical to accepted Iterations 7 and 8A. Iteration 8B is a renderer/art recomposition only; authoritative simulation state and behavior did not change.

## What Iteration 8B changed

The habitat's major visual masses are now authored through `display/art/` instead of being assembled primarily from room-specific `rect(...)` code in `display/web/app.js`.

The accepted room composition includes authored:

- full room shell, wall/floor material planes, trim, and sparse structural irregularity;
- richer exterior/window view with layered foliage and cool distance colors;
- deep window alcove, asymmetric curtains, sill, and perch;
- sleeping nook with stronger timber/cloth planes and asymmetrical domestic detail;
- broad living rug with bounded woven motifs and preserved negative space;
- collection shelf and real foreground shelf lips;
- activity desk, papers, plant, material accents, and foreground desk lip;
- water and food bowls;
- conditional authored window-perch foreground occlusion.

The room still uses the accepted `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT / ALWAYS_FRONT` scene grammar. Major furniture is in `STRUCTURE`, rug/floor/history in `SURFACE`, bowls and located environmental events in `WORLD`, Moss in `ACTORS`, and true furniture lips in `FRONT`.

## Palette and material direction

The palette bank now implements the intended richer saturated-natural language rather than the deliberately conservative 8A values. It adds deeper/warm timber roles, stronger vegetation ramps, distinct cloth blues, terracotta, brass, glass-light, stone, and selective flower/accent roles while preserving dawn/day/dusk/night variants.

The visual direction remains earthy and restrained rather than neon: chromatic darks, warm wood, stronger greens, clearer cool exterior values, cream highlights, and selective amber/terracotta accents. Material families remain explicit and palette-addressable.

## Persistent world-state presentation

8B preserves canonical state-driven overlays rather than baking fake history into the redraw:

- path wear remains driven by authoritative habitat history;
- sleeping-nook compression/creased aftermath remains history-driven;
- activity-corner paper/clutter buildup remains history-driven;
- window smudges/wet marks remain history/weather-driven;
- sunlight, bird, rain, thunder, moth, leaf contact, and other event presentation remain tied to canonical event state;
- object positions and Moss navigation remain continuous `terrarium.spatial.v1` coordinates.

The art grid remains composition grammar only. No tile navigation, renderer-owned targeting, hidden behavior, or presentation-only backstory was introduced.

## Browser / temporal UAT

Real production-browser UAT used isolated `/tmp/terrarium-iteration8b-uat` state and the 8B deterministic fixture pack.

Final evidence includes dawn clear, day clear fresh/lived, dusk mist, night rain lived-in, object inspection, sleep transition, moth engagement, continuity, and RAF pacing. All sampled rasters preserve exact **400×240 → 800×480** 2× nearest-neighbor scaling with smoothing disabled and zero scale-error blocks.

Key final results:

- deterministic fresh-day repeat: `fnv1a32:29e7d52d` reproduced exactly;
- inspect sequence: **11 samples / 7 distinct rasters**;
- sleep transition: **11 / 9 distinct rasters**;
- moth engagement: **11 / 8 distinct rasters**;
- continuity probe: **0 px** jump;
- RAF probe: **110 frames / 1816.6 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms;
- zero browser console errors were observed; the harness reported one repeated non-fatal warning during some sequence/probe loads.

The promoted `grid-quantized-temporal-render-auditor-r1` binary is still not directly exposed by the frozen MCP/Lab surface. No substitute capability was forged; relevant rejection classes were exercised through deterministic raster, exact-scale, continuity, and RAF checks.

## Validation

- pytest: **46/46 PASS**;
- Python-3.10 grammar guard: **35 sources PASS**;
- JavaScript syntax: **PASS**;
- authored manifest/palette/asset schema and bounds validation: **PASS**;
- technical evaluator / append-only chain / restart / exact replay: **PASS**;
- behavior, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- spatial, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- coherence, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- habits, seeds 1701/1702/42/999 at 10,080 steps: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- deterministic production-browser art/temporal UAT: **PASS**;
- combined Iteration-8B regression matrix: **PASS**.

Canonical Moss was not reset, replaced, migrated, or used as a development fixture.

## SBC conclusion

No reusable SBC substrate deficiency was exposed. 8B required Terrarium-specific palette tuning, authored art, room composition, and renderer layering; the existing project/browser/evaluation substrate was sufficient.

Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18 decision: NO.**

## Next: Iteration 8C — Moss Sprite Overhaul

Bring Moss up to the room's authored visual maturity without changing the accepted semantic action vocabulary or timing authority:

- replace remaining procedural body/head/leg assembly with true authored low-frame sprites;
- keep readable silhouette, floppy asymmetrical ears, clear muzzle/head direction, planted feet, restrained tail acting, and strong object/furniture contact;
- cover walk, inspect, nudge, pickup, carry, place, loaf, groom, stretch, react, window watch, sleep transition, curled sleep, and wake;
- keep stillness valid and avoid random fidgeting or smooth skeletal tweening;
- preserve all target, navigation, event, habit, possession, and object authority in the world engine.

Success means Moss looks like a specific hand-authored inhabitant who belongs in the accepted 8B room.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Any host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
