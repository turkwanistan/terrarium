# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8F: Seasonal Terrarium**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-28-pixel-art-overhaul-iteration8f.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8f.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8f-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8f-browser-uat.json`
- seasonal evaluation: `artifacts/pixel-art-overhaul-iteration8f-seasons.json`
- atmosphere regression: `artifacts/pixel-art-overhaul-iteration8f-atmosphere.json`
- art-direction matrix / fixtures: `artifacts/iteration8f-art-direction-matrix.json` / `artifacts/iteration8f-art-direction-fixtures.json`
- accepted snapshot: `20260828T160757100074Z-pixel-art-overhaul-iteration8f`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `51d574524e710025428d615dadfcf48fb30e826a03b7b58126ce54784ea9b6ca`
- renderer JS SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art tree SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`
- authored assets: **83 total / 46 Moss / 13 object-state / 5 new seasonal environment assets**
- behavior rules: `terrarium-rules-v8-seasonal-world`
- seasonal schema: `terrarium.seasons.v1`
- seasonal cadence: **21 real days per season / 7 real days per stage / 84 real days per full cycle**
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- object affordances: `terrarium.object-affordances.v1`
- situational events: `terrarium.situational-events.v1`
- habits: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

The accepted 8F semantic frame differs from accepted 8E in exactly one recursive location: the new top-level `season` projection. Existing behavior/object/history state is otherwise byte-equivalent in the deterministic comparison frame.

## What Iteration 8F changed

Season is now canonical long-horizon world state rather than renderer uptime or accelerated world-day math. The production world uses a real-time observation against a stored epoch while deterministic tests/replay use explicit or derived observation time. Existing worlds migrate conservatively on their first ordinary post-upgrade tick: the epoch begins at first observation with `migration_origin=neutral-existing-world`, so no fabricated historical seasons are introduced.

The cadence is intentionally slow and discrete:

- **spring / summer / autumn / winter**;
- **21 real days per season**;
- **early / full / late** stages of **7 real days** each;
- **84 real days per full cycle**.

The renderer adds restrained seasonal treatment without changing room identity: fresh spring greens/blossoms, denser summer canopy, progressively thinning rust autumn foliage, and sparse pale winter branches/exterior. Four finite seasonal material treatments compose with existing canonical weather, then existing local warm light. Missing canonical season fails neutral; the browser never invents spring.

Season does **not** currently command Moss, change action weighting, alter situational-event occurrence, or create new canonical weather such as snow. Those remain deliberate boundaries.

## Deployment / canonical migration

The accepted code was deployed against the existing host-owned canonical world at `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live`. The prior process was stopped without deleting or replacing runtime storage, then `scripts/run_lan.sh` restarted the same world on port 8765.

Post-deploy canonical observation:

- original `created_at`: **2026-08-27T03:45:50.032660Z** preserved;
- rules version: `terrarium-rules-v8-seasonal-world`;
- seasonal migration origin: `neutral-existing-world`;
- seasonal epoch: **2026-08-28T16:33:07.468419Z**;
- observed season/stage: **spring / early**;
- verified tick/event count: **78,637 / 78,637**, continuing existing history rather than resetting;
- canonical/replayed state SHA256 at verification: `b9a4ff9a7c1524d4abe34ac2407c0e6988fa7ea04fd2b05da7d400ef5787a277`;
- exact replay: **PASS**;
- live browser later showed canonical season projection and `dusk-spring` palette at tick **78,650**.

Before restart, the new renderer was also tested against the still-running 8E engine: because no canonical season existed, it correctly retained the neutral accepted palette instead of fabricating a season.

## Browser / temporal UAT

The isolated production-renderer pack covers all four clear-day seasons; spring/summer/autumn/winter night/weather contexts; autumn early/full/late progression; activity/object/event combinations; autumn→winter transition; and winter warm-local-light contrast.

- four clear-day seasonal rasters: **all distinct**;
- autumn early/full/late rasters: **all distinct**;
- seasonal weather combinations: **distinct**;
- deterministic spring repeat: `fnv1a32:ba902b2d` → exact repeat;
- exact 400×240 → 800×480 2× scaling: **PASS**, zero scale-error blocks;
- continuity: **0 px** jump after 1000 ms interruption;
- RAF: **181 frames / 3000 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero >34 ms / >50 ms intervals;
- visual review: **ACCEPTED**.

## Validation

- pytest: **55/55 PASS**;
- Python-3.10 grammar: **38 sources PASS**;
- JavaScript syntax: **PASS**;
- authored assets: **83/83 PASS**;
- dedicated Iteration-8F season evaluator: **PASS**;
- Iteration-8E atmosphere regression: **PASS**;
- technical evaluator at 10,080 events / append-only chain / restart / exact replay: **PASS**;
- behavior, spatial, coherence, habits: seeds **1701 / 1702 / 42 / 999**, 10,080 steps each: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- Iteration-8D object-affordance regression: **PASS**;
- deterministic production-browser UAT: **PASS**;
- combined Iteration-8F regression matrix: **PASS**;
- post-deploy canonical restart/migration/replay/browser verification: **PASS**.

## SBC conclusion

The existing canonical-state/replay substrate, authored-art pipeline, deterministic temporal fixtures, browser evidence path, evaluator framework, and promoted Optiplex capabilities were sufficient. No genuinely reusable substrate deficiency was exposed. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

**Gen18: NO**

## Next: Iteration 9 — Emergent Situations and Consequence Memory

Compose the now-richer world state across time: let prior event outcomes, object displacement/state, arrangements, learned habits, persistent traces, and environmental/seasonal context create later opportunities and multi-stage situations without scripted quests or a generic planner.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
