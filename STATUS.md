# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8E: Atmospheric World**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-28-pixel-art-overhaul-iteration8e.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8e.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8e-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8e-browser-uat.json`
- atmosphere evaluation: `artifacts/pixel-art-overhaul-iteration8e-atmosphere.json`
- art-direction matrix / fixtures: `artifacts/iteration8e-art-direction-matrix.json` / `artifacts/iteration8e-art-direction-fixtures.json`
- accepted snapshot: `20260828T123835255741Z-pixel-art-overhaul-iteration8e`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`
- renderer JS SHA256: `c46cc4722cade0585f7ef4af122e4801debaa50c6c8eddf054e511118f307b85`
- authored-art tree SHA256: `5daacbe022e34b807d2008ee37037bef998b99abe77d8eafde157bcf599faae4`
- authored assets: **78 total / 46 Moss / 13 object-state / 5 new ambient**
- behavior rules: `terrarium-rules-v7-object-identity`
- object affordances: `terrarium.object-affordances.v1`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- habits: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

The semantic frame hash is **identical to accepted 8D** because 8E changed no authoritative simulation source. `git diff -- terrarium` was empty at acceptance.

## What Iteration 8E changed

Atmosphere is now a deterministic presentation system distinct from situational events. The accepted renderer adds:

- three authored window foliage depth layers with different held-step timing;
- restrained authored curtain edge motion;
- per-trace rain timing and slow pane runoff;
- discrete mist drift;
- localized clear-day light motes;
- slow hard-edged branch-shadow movement;
- infrequent water-bowl shimmer;
- hard-edged warm nook/desk night-light treatment;
- finite whole-scene rain/mist palette treatments.

Ambient clocks derive from canonical `world_minutes`; deterministic fixture timestamps extend that clock only inside development temporal mode. Ambient motion does not create events, attract Moss, mutate habits, add planner state, or write persistent consequences.

## Deliberate restraint

The accepted pass did **not** add a drifting-leaf particle field, looping ambient birds/insects, snow before seasonal authority exists, fireplace/flame animation, full-room random sparkle/motes, smooth gradients, bloom, blur, or fog masks. These were rejected/deferred because the smaller system already makes still scenes feel temporal without competing with Moss.

## Browser / temporal UAT

Final production-browser UAT used isolated `/tmp/terrarium-iteration8e-final`; canonical Moss was never reset or used as a fixture.

Ten 8E contexts cover clear day/night, warm night light, rain, mist, window focus, stationary Moss, walking Moss, situational-event coexistence, sleep, and object interaction. The long-observation timestamps reach **56 seconds**.

- deterministic clear-day sequence: **exact repeat**;
- each required sequence: **7–9 distinct rasters / 9 samples**;
- every sampled sequence: **0 scale-error blocks**, exact 400×240 → 800×480 2× nearest-neighbor;
- continuity: **0 px** jump;
- RAF: **182 frames / 3016.6 ms**, p50 **16.7 ms**, p95/max **16.8 ms**, zero >34 ms / >50 ms intervals;
- browser console errors: **0**; the same benign temporal-fixture warning as prior accepted UAT remains;
- ambient presentation remains below `ACTORS`/foreground priority and is never promoted to `ALWAYS_FRONT`.

## Validation

- pytest: **51/51 PASS**;
- Python-3.10 grammar: **37 sources PASS**;
- JavaScript syntax: **PASS**;
- authored assets: **78/78 PASS**;
- dedicated Iteration-8E atmosphere evaluator: **PASS**;
- technical evaluator at 10,080 events / append-only chain / restart / exact replay: **PASS**;
- behavior, spatial, coherence, habits: seeds **1701 / 1702 / 42 / 999**, 10,080 steps each: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- Iteration-8D object-affordance regression: **PASS**;
- deterministic production-browser UAT: **PASS**;
- combined Iteration-8E regression matrix: **PASS**.

## SBC conclusion

The existing authored-art pipeline, temporal fixtures, browser evidence path, renderer layer system, evaluator framework, and Optiplex/SBC capabilities were sufficient. No reusable substrate deficiency was exposed. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

**Gen18: NO**

## Next: Iteration 8F — Seasonal Terrarium

Add a canonical deterministic seasonal timescale substantially slower than the accelerated day, then coordinate long-horizon exterior foliage, palette, lighting, weather/particles, ambient life, and selected interior accents without erasing the familiar room or compromising replay/migration.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
