# START HERE

Terrarium is the real project that followed the accepted Self-Building Computer Generation 17 pilot. It now evolves as normal product development. Repository state, live runtime state, tests/evaluators, and accepted evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 2: Sprite Acting and Environmental Detail**

- history: `history/2026-08-27-pixel-art-overhaul-iteration2.md`
- evidence: `artifacts/pixel-art-overhaul-iteration2.json`
- snapshot: `snapshots/dev/20260827T192116263284Z-pixel-art-overhaul-iteration2`
- seed/tick: **1701 / 698**
- semantic frame SHA256: `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`
- renderer JS SHA256: `7b03f5554d121fa8dec5481e8078547baac3f28589968a4da9570b3a0925e0e6`

The semantic frame is unchanged from Iteration 1; the checkpoint is renderer/art only.

## Read before editing

Read `STATUS.md`, `ART_DIRECTION.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, and the latest history entry. `ART_DIRECTION.md` is the accepted visual authority.

## Non-negotiable presentation contract

- canonical semantic/reference frame remains **800×480**;
- renderer authors art on **400×240**;
- display is exact **2× nearest-neighbor**;
- image smoothing stays off;
- renderer may stage/interpolate canonical actions but may not own behavior, targets, object state, history, time, or world decisions;
- heartbeat remains **3 real seconds**, world advances **1 minute/heartbeat**, full day is about **72 real minutes**.

Moss is a compact brown floppy-eared dog with no default glasses. Iteration 2 adds explicit authored key-pose acting for walk, inspect, pickup/carry/place, window watching, rest, sleep, and wake. The room uses sparse clustered material detail and hard pixel-native depth/occlusion rather than large primitive rectangles or procedural noise.

## Promoted objective capabilities

- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Use the grid specialization only when the renderer declares integer-grid quantization and supplies continuous presentation anchors. It still rejects teleport, reversal, frozen motion, facing errors, scene jitter, attachment errors, causality failures, bad settling, RAF stalls, and false grid declarations. None of these capabilities is an aesthetic oracle.

## Fresh-session procedure

1. Inspect Git status/log/tracking and active services; preserve unrelated work and canonical runtime state.
2. Read the current docs/history/evidence above.
3. Run `python -m pytest -q` with project write permission, `node --check display/web/app.js`, `python evaluations/evaluate_technical.py`, and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
4. Preserve Python 3.10 syntax compatibility.
5. For renderer timing changes, run deterministic browser scenarios, exact raster checks, the appropriate promoted temporal auditor, continuity probe, and real RAF probe.
6. Inspect the actual 800×480 Canvas; human judgment owns art quality.
7. If behavior semantics change, evaluate them separately and run the promoted behavior auditor instead of hiding the change in renderer work.
8. For an accepted visible iteration: one bounded evidence artifact, exactly one meaningful development snapshot, concise state/history updates, one coherent commit, mediated push attempt, and canonical deployment verification.

## Current acceptance baseline

Iteration 2 passed **22/22 tests**, exact replay hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`, unchanged seed-1701/500 behavior (**186 decisions + 314 continuations**), 17 deterministic browser scenarios / 187 exact-scale samples, 0 px continuity jump, byte-identical repeated walk capture, real RAF max 16.8 ms, and the promoted grid-aware temporal auditor **9/9**.

## SBC policy

Normal Terrarium needs drive future SBC evolution. Iteration 2 required no new capability and no platform change. Do not label later work Gen18 unless a genuine reusable substrate deficiency is demonstrated and cannot reasonably be solved within Terrarium or Capability Forge.
