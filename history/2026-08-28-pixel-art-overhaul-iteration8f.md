# Pixel-Art Overhaul — Iteration 8F: Seasonal Terrarium

**Status: ACCEPTED — 2026-08-28**

Iteration 8F makes long real-world time part of Terrarium's canonical world and visual identity without changing Moss's behavior authority.

## Canonical season model

`terrarium.seasons.v1` stores a real-time epoch and deterministic derived season/stage. The accepted cadence is spring → summer → autumn → winter, **21 real days each**, with discrete **early / full / late** 7-day stages. Production observes wall-clock UTC; deterministic engines/tests can supply or derive deterministic observation time. Renderer uptime is never authority.

Existing worlds migrate on their first ordinary post-upgrade tick. The migration starts spring/early at that first observation with `migration_origin=neutral-existing-world`; it does not pretend the world experienced seasons before the feature existed. The state change is part of the ordinary hashed event/state chain, so restart and replay remain exact.

## Visual implementation

Five authored environment assets were added for spring blossom, summer canopy, autumn leaves, winter view, and winter branches, bringing the manifest to **83 assets**. Four finite material treatments provide seasonal color identity before existing weather and local-light treatment.

The room remains structurally stable. Spring adds fresh greens/blossoms; summer adds denser canopy; autumn uses rust foliage that thins across early/full/late; winter replaces dense foliage with a sparse pale exterior and branches. Winter night strengthens the accepted cool-outside/warm-shelter contrast. No gradients, bloom, blur, random particle fields, seasonal crossfades, holidays, or canonical snow were added.

A critical UAT boundary was fixed before acceptance: a renderer connected to a frame with no canonical season now stays on the neutral accepted 8E palette instead of silently assuming spring.

## Behavior / authority preservation

Season is additive context only in 8F. Controlled evaluation confirms contrasting seasons do not alter Moss's behavior state. Existing weather authority/signature is unchanged. Situational events, object affordances, habits, route/contact authority, object state, and history remain under their existing canonical systems.

The deterministic seed-1701/tick-10080 semantic frame SHA256 is `51d574524e710025428d615dadfcf48fb30e826a03b7b58126ce54784ea9b6ca`. Recursive comparison against accepted 8E found exactly one semantic delta: top-level `season`.

## Evaluation

- pytest: **55/55 PASS**;
- Python-3.10 grammar: **38 sources PASS**;
- JavaScript syntax: **PASS**;
- authored assets: **83/83 PASS**;
- dedicated seasonal evaluator: **PASS**;
- Iteration-8E atmosphere regression: **PASS**;
- technical evaluator: **10,080 events, append-only chain, restart, exact replay PASS**;
- behavior/spatial/coherence/habits: seeds **1701 / 1702 / 42 / 999**, **10,080 steps each**, all PASS;
- repertoire/situations/object-affordances: **PASS**;
- 63-scenario art-direction/temporal fixture pack generated;
- browser UAT across all four seasons, autumn progression, weather, night, activity, events, object interactions, sleep, and transition: **PASS**;
- deterministic spring browser hash repeats exactly at `fnv1a32:ba902b2d`;
- exact 2× scaling: **PASS**, zero scale-error blocks;
- continuity: **0 px** jump;
- RAF: **181 / 3000 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero long-frame violations.

Accepted deterministic snapshot: `20260828T160757100074Z-pixel-art-overhaul-iteration8f`

- frame SHA256: `51d574524e710025428d615dadfcf48fb30e826a03b7b58126ce54784ea9b6ca`
- renderer SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`

## Canonical deployment

The live OptiPlex world was restarted against the same user-owned `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` store. No database reset or replacement occurred.

Verified post-deploy:

- original world `created_at`: `2026-08-27T03:45:50.032660Z`;
- tick / event count: `78637 / 78637`;
- rules: `terrarium-rules-v8-seasonal-world`;
- season schema: `terrarium.seasons.v1`;
- migration: `neutral-existing-world`;
- epoch: `2026-08-28T16:33:07.468419Z`;
- current state at verification: `spring / early`;
- replay: **ok**;
- canonical and replayed state SHA256: `b9a4ff9a7c1524d4abe34ac2407c0e6988fa7ea04fd2b05da7d400ef5787a277`.

A subsequent live browser inspection at tick 78,650 exposed canonical `season` and the expected `dusk-spring` palette.

## SBC / next step

No reusable substrate deficiency appeared. Existing Terrarium/Optiplex capabilities were sufficient; the frozen MCP surface and Self-Building Computer were not modified. **Gen18: NO.**

Next product iteration: **Iteration 9 — Emergent Situations and Consequence Memory**.
