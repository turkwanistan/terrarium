# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 5: Long-Horizon Preferences and Habit Formation**

- history: `history/2026-08-27-pixel-art-overhaul-iteration5.md`
- evidence: `artifacts/pixel-art-overhaul-iteration5.json`
- snapshot: `snapshots/dev/20260827T222822886488Z-pixel-art-overhaul-iteration5`
- seed/tick: **1701 / 10080**
- frame SHA256: `a275783dc04234b1da10d8bb6dd1b8a2bcaaeba134ee5ae07f0062687cf51290`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- behavior rules: `terrarium-rules-v4-long-horizon-habits`
- behavior context: `terrarium.behavior-context.v1`
- habit profile: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

Read `STATUS.md`, `ART_DIRECTION.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, bounded routine context, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes and animate authored poses but may not invent navigation, intent, or targets;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior rules: `terrarium-rules-v4-long-horizon-habits`; RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry: `terrarium.spatial.v1`.

## Behavioral law after Iteration 5

Iteration-4 short-horizon coherence remains intact: at most four recent zones, four recent objects, and one current routine intent. On top of that, canonical `terrarium.habits.v1` accumulates slow bounded zone, object, and time-of-day-context affinity from actual experience. It is a preference memory, not personality scripting or a needs system.

Reinforcement saturates, old evidence decays slightly, preference influence phases in slowly, and every weighted choice retains an exploration floor. Recent-zone/object inhibition still prevents immediate ping-pong and fixation. Habits may bias future choices but never bypass reachability, possession/session continuity, spatial authority, or environmental constraints.

Existing worlds migrate to a documented neutral habit baseline without resetting Moss or fabricating historical preferences. Canonical event history remains authoritative; the renderer receives behavior consequences, not hidden personality labels.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, technical/behavior/spatial/coherence/long-horizon-habit evaluators, exact replay, deterministic browser captures, continuity + RAF probes, applicable promoted temporal audits, and real 800×480 browser inspection. Treat coherence metrics as diagnostics, not targets to game.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

The promoted behavior auditor's executable capsule is not currently materialized in the disposable Lab filesystem; do **not** forge a duplicate merely to recreate it. Terrarium's product-specific behavior/coherence evaluators remain authoritative for this checkpoint, and the existing promoted temporal auditor remains usable.

Do not invent Gen18 by cadence. Terrarium-specific needs remain inside Terrarium unless evidence demonstrates a reusable SBC substrate deficiency.
