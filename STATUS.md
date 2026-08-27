# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 2: Sprite Acting and Environmental Detail**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration2.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration2.json`
- accepted snapshot: `20260827T192116263284Z-pixel-art-overhaul-iteration2`
- deterministic seed/tick: **1701 / 698**
- semantic frame SHA256: `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`
- renderer JS SHA256: `7b03f5554d121fa8dec5481e8078547baac3f28589968a4da9570b3a0925e0e6`

The semantic frame is byte-identical to Iteration 1. This checkpoint changes presentation only: authoritative world state, object positions, behavior decisions, history, world clock, 3-second heartbeat, 1-world-minute heartbeat advance, ~72-real-minute day, and deterministic weather cadence are unchanged.

## What Iteration 2 established

Moss is now an authored pixel sprite rather than a generic block body with procedural deformation. The renderer has explicit acting stages for idle, four-keyframe locomotion, inspect, pickup anticipation/contact/recovery, carry, place anticipation/contact/release/recovery, window watching, rest, sleep curl/settle, and wake/unfold. Ear, tail, gaze, planted feet, chest paws, and contact paws change in discrete authored poses. Animation remains renderer-only interpretation of canonical actions.

The room received the same craft pass: deeper window casing and sill, cloth folds, structured bed/blanket/pillow, woven rug, recessed shelf bays/lips/books/trinkets, desk top/apron/legs/drawer, bowls with rims/interiors, sparse plaster and floor material clusters, planted furniture feet, and stronger hard-edged grounding/occlusion. Persistent bedding, window, path, activity, and object-history marks still derive only from authoritative frame data.

Lighting/weather remain finite palette-driven pixel changes. Rain is sparse and window-localized; no gradients, blur, smooth vector lighting, random camera motion, or high-resolution-then-pixelated rendering were introduced.

## Pixel-art contract

`ART_DIRECTION.md` remains visual authority.

- semantic/reference frame: **800×480**;
- internal art surface: **400×240**;
- presentation: exact integer **2× nearest-neighbor**;
- smoothing: disabled on both canvases;
- all sampled browser frames: exact 2×2 duplication with zero scale errors;
- human inspection of the actual 800×480 Canvas remains the aesthetic acceptance gate.

## Temporal / regression acceptance

- pytest: **22/22 PASS**;
- Python 3.10 syntax guard: **PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **PASS**;
- exact replay: **PASS**, canonical/replayed hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator seed 1701 / 500: **PASS**, **186 decisions + 314 continuation ticks**, all 6 objects moved;
- deterministic browser reel: **17 scenarios / 187 sampled frames**, exact 2× contract in every sample;
- walk vocabulary observed: keyframes **0, 1, 2, 3**;
- repeated left-walk capture: byte-identical SHA256 `95a2f2c0f7bb551023ff0852302e316cb5d10403ea7b97f1489e9b0395348ddf`;
- continuity interruption jump: **0 px**;
- real RAF: **16.5 ms min / 16.7 ms p50 / 16.8 ms p95 / 16.8 ms max**, zero >34 ms and zero >50 ms stalls;
- promoted `grid-quantized-temporal-render-auditor-r1`: **9/9 PASS**, zero quantization-contract mismatches;
- real 800×480 visual inspection: **accepted**.

## SBC conclusion

Existing deterministic capture/evaluation infrastructure plus promoted `grid-quantized-temporal-render-auditor-r1` were sufficient. No new capability was forged, no SBC platform code changed, and no reusable substrate deficiency was demonstrated. **Gen18 is not warranted.**

## Runtime / Git safety

Canonical Moss state is user-owned and outside Git. Development/evaluation worlds are disposable. Only `data/.gitkeep` is tracked; runtime SQLite/event files must remain uncommitted. Static renderer changes are served directly from `display/web/*` with no-cache and do not require a ceremonial world-process restart.

## Next product work

Use direct UAT of Iteration 2 to choose the next normal Terrarium target. Preserve the pixel-art contract and semantic/render authority split. If remaining visible problems are spatial/behavioral (for example pathing through furniture or implausible resting locations), treat them as a separate navigation/affordance iteration rather than hiding semantic changes inside art code.
