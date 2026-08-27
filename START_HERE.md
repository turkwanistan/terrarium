# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 3: Spatial Coherence and Physical Acting**

- history: `history/2026-08-27-pixel-art-overhaul-iteration3.md`
- evidence: `artifacts/pixel-art-overhaul-iteration3.json`
- snapshot: `snapshots/dev/20260827T204232352544Z-pixel-art-overhaul-iteration3`
- seed/tick: **1701 / 698**
- frame SHA256: `fe7ffd8dbefc56144c7af673a810339f136ae6f08db580cf80bc8b819f0996a9`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- spatial schema: `terrarium.spatial.v1`

Read `STATUS.md`, `ART_DIRECTION.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes and animate authored poses but may not invent navigation or targets;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior RNG stays `terrarium-rules-v2-action-pacing`; geometry is independently versioned `terrarium.spatial.v1`.

## Spatial law after Iteration 3

Moss uses authored floor bounds, blocker rectangles, a small deterministic waypoint graph, physical approach anchors, reachable interaction contact points, and a supported bed anchor. Sleep is only valid at the supported bed position. Wake exits through the bed gate before another decision. Window, shelf, desk, and object actions occur from reachable sides. Multi-turn routes are authoritative event data and deterministic under replay.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, technical/behavior/spatial evaluators, exact replay, deterministic browser captures, continuity + RAF probes, applicable promoted temporal audits, and human inspection of the actual 800×480 Canvas. Use the promoted behavior auditor whenever semantic behavior changes.

Promoted capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific needs remain inside Terrarium unless evidence demonstrates a reusable SBC substrate deficiency.
