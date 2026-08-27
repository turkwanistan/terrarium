# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 4: Behavioral Intent and Routine Coherence**

- history: `history/2026-08-27-pixel-art-overhaul-iteration4.md`
- evidence: `artifacts/pixel-art-overhaul-iteration4.json`
- snapshot: `snapshots/dev/20260827T212849313774Z-pixel-art-overhaul-iteration4`
- seed/tick: **1701 / 698**
- frame SHA256: `aee7d6188523b4f3cf1539d653a8816e2dc87ae10a86d62ddb3d1b1ac9e3df9f`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- behavior rules: `terrarium-rules-v3-routine-coherence`
- behavior context: `terrarium.behavior-context.v1`
- spatial schema: `terrarium.spatial.v1`

Read `STATUS.md`, `ART_DIRECTION.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, bounded routine context, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes and animate authored poses but may not invent navigation, intent, or targets;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior RNG: `terrarium-rules-v3-routine-coherence`; geometry: `terrarium.spatial.v1`.

## Behavioral law after Iteration 4

Moss has a small deterministic short-horizon context, not a general utility-AI framework: at most four recent zones, four recent objects, and one current routine intent. Movement should follow an intention; arrivals normally settle before new travel; window visits become viewing sessions; inspection can continue into same-object pickup; carrying follows one chosen delivery target; placement has recovery; wake has recovery and supported egress. Recent zones/objects inhibit obvious ping-pong and fixation.

Favorite spots remain authored uses of the compact spatial graph rather than a navigation grid. Canonical event history remains the long-term memory; hot behavior state stays bounded.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, technical/behavior/spatial/coherence evaluators, exact replay, deterministic browser captures, continuity + RAF probes, applicable promoted temporal audits, and real 800×480 browser inspection. Treat coherence metrics as diagnostics, not targets to game.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

The promoted behavior auditor's executable capsule is not currently materialized in the disposable Lab filesystem; do **not** forge a duplicate merely to recreate it. Terrarium's product-specific behavior/coherence evaluators remain authoritative for this checkpoint, and the existing promoted temporal auditor remains usable.

Do not invent Gen18 by cadence. Terrarium-specific needs remain inside Terrarium unless evidence demonstrates a reusable SBC substrate deficiency.
