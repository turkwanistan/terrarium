# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 4: Behavioral Intent and Routine Coherence**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration4.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration4.json`
- accepted snapshot: `20260827T212849313774Z-pixel-art-overhaul-iteration4`
- deterministic seed/tick: **1701 / 698**
- semantic frame SHA256: `aee7d6188523b4f3cf1539d653a8816e2dc87ae10a86d62ddb3d1b1ac9e3df9f`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- behavior context schema: `terrarium.behavior-context.v1`
- behavior rules: `terrarium-rules-v3-routine-coherence`
- spatial schema: `terrarium.spatial.v1`

## What Iteration 4 established

Moss no longer chooses each meaningful action as an isolated weighted sample. A deliberately small host-owned routine context now remembers only the last four zones/objects plus one bounded current intent. Arrival, window, object, placement, sleep, and wake states bias the next few decisions toward plausible continuation while preserving deterministic autonomy.

Movement is normally the consequence of an intent. Destination selection inhibits immediate zone ping-pong, favors a few authored familiar spots, and commits carried objects to one delivery destination. Inspecting an object strongly favors continuing with that same object; after a completed object session Moss briefly inhibits returning to the same prop when another local choice exists. Arrival, window watching, placement, rest, sleep, and wake have longer readable dwell/recovery commitments.

Legacy worlds acquire `terrarium.behavior-context.v1` through ordinary deterministic evolution. Existing possession, object movement/inspection counts, event history, and canonical Moss state are not reset or rewritten.

## Acceptance

- pytest: **28/28 PASS**;
- Python 3.10 grammar guard: **PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **PASS**, including append-only event chain, restart persistence, and exact snapshot+event replay;
- behavior evaluator seed 1701 / 500: **PASS**, 155 decisions + 345 continuations, 10 action classes, all 6 objects moved;
- spatial evaluator seed 1701 / 500: **PASS**, 49 routed actions, 33 multi-segment routes, 21 carried routes, 48 targeted interactions, **0 blocker intersections**, **0 invalid awake endpoints**;
- Iteration-4 coherence evaluator seed 1701 / 2000: **PASS** and deterministic duplicate equality;
- multi-seed coherence robustness: **1701 / 1702 / 42 / 999 all PASS**;
- real browser 3-second UAT exposed a coherent unscripted sequence: window watch → linger → inspect amber leaf → carry same leaf → direct shelf delivery → settle/place → sleep;
- real RAF: **16.5 ms min / 16.7 ms p50 / 16.7 ms p95 / 16.8 ms max**, zero >34 ms / >50 ms;
- promoted `temporal-render-auditor-r1` on the fresh RAF capture: **PASS**, 0 critical failures;
- renderer code is byte-identical to Iteration 3, so accepted pixel-grid rendering/acting mechanics remain unchanged.

### Before → after, seed 1701 / 2000 ticks

- decisions/hour: **22.20 → 17.49**;
- movement decisions/hour: **5.19 → 3.42**;
- cross-room moves/hour: **2.22 → 1.26**;
- average zone dwell: **10.20 → 15.04 ticks**;
- median zone dwell: **10 → 13 ticks**;
- post-arrival linger: **89.6% → 98.2%**;
- inspect → same-object carry within two decisions: **18.7% → 83.0%**;
- window arrival → watch within two decisions: **60.0% → 92.9%**;
- post-place linger: **87.0% → 100%**;
- wake → quiet recovery: **39.3% → 100%**;
- non-delivery immediate movement reversal rate after change: **3.0%**;
- chosen object delivery completion: **100%**;
- calm visible timeline share: **69.5% → 74.0%**.

Metrics are diagnostic gates, not personality targets. The retained behavior remains probabilistic and deterministic rather than a scripted routine list.

## Pixel-art / pacing invariants

`ART_DIRECTION.md` remains visual authority. Internal art stays **400×240**, displayed as exact **2× nearest-neighbor 800×480** with smoothing off. The heartbeat remains **3 real seconds**, world advance **1 minute/heartbeat**, and a full day remains ~**72 real minutes**. Host-side state owns behavior and routes; renderer interpolation remains presentation-only.

## SBC conclusion

The missing property was Terrarium-specific short-horizon coherence, so it was evaluated inside Terrarium with `terrarium.behavior-coherence-evaluation.v1`. Existing SBC infrastructure and the promoted temporal auditor were sufficient; no Capability Forge work, SBC mutation, MCP growth, or **Gen18** was justified. Unrelated dirty Self-Building Computer state was not touched.

## Runtime / Git safety

Canonical Moss state remains user-owned and outside Git. Only `data/.gitkeep` may be tracked from runtime storage. Deployment must preserve the existing canonical runtime directory, event chain, seed, object history, and SQLite database. A disposable development world is never a substitute for canonical Moss.
