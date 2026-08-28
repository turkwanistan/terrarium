# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 9: Emergent Situations and Consequence Memory**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-28-pixel-art-overhaul-iteration9.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration9.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration9-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration9-browser-uat.json`
- consequence evaluator: `artifacts/pixel-art-overhaul-iteration9-consequences.json`
- accepted snapshot: `20260828T182004989725Z-pixel-art-overhaul-iteration9`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `33cced839bb3c2067da01b786c705bf5e3a2a645086e4cfdabee3748ee93f17a`
- renderer JS SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art tree SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`
- behavior rules: `terrarium-rules-v9-consequence-memory`
- consequence schema: `terrarium.consequence-memory.v1`

## What Iteration 9 changed

A bounded canonical causal index now remembers unresolved consequences from situational aftermath, persistent traces, arrangements, displacement, and nesting. It is capped at 12 hot entries and does not replace or scan the full append-only event ledger on every decision. Equivalent visible worlds may carry different authoritative causal histories and later diverge while remaining individually deterministic.

A later opportunity reuses existing behavior machinery: recognize (`react`) → ordinary route/approach (`walk`) → engage (`inspect` / `loaf` / `rest` / `look_outside`) → bounded recovery. One unresolved consequence produces at most one revisit; equivalent new causes reinforce/merge before resolution rather than creating permanent loops.

## Canonical deployment

The accepted code runs against the existing user-owned `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` world. No database reset/replacement occurred.

Post-deploy verification:

- original `created_at`: **2026-08-27T03:45:50.032660Z** preserved;
- rules: `terrarium-rules-v9-consequence-memory`;
- consequence migration: `neutral-existing-world`; no fabricated entries/counters;
- existing season epoch: **2026-08-28T16:33:07.468419Z** preserved;
- season/stage: **spring / early**;
- tick/event: **80,715 / 80,715**;
- exact replay: **PASS**;
- canonical/replayed state SHA256: `e6e5c57d8c49444831a1b765f70e01c31221b9fba9a50138a60a2b344eeb76b3`.

## Validation

- pytest: **60/60 PASS**;
- Python-3.10 grammar: **41 sources PASS**;
- JavaScript syntax: **PASS**;
- technical exact replay at 10,080 events: **PASS**;
- behavior/spatial/coherence/habits: seeds **1701 / 1702 / 42 / 999**, 10,080 each: **PASS**;
- repertoire / situations / object-affordances / atmosphere / seasons: **PASS**;
- dedicated four-seed consequence evaluator: **PASS**;
- controlled same-present/different-history future divergence: **PASS**, divergence tick **627**;
- hot consequence memory bounded at **12**: **PASS**;
- production renderer UAT of recognize→approach→engage: **PASS**.

## SBC conclusion

No reusable substrate deficiency was found. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18: NO.**

## Next: Iteration 10 — Causal Composition and Situation Chaining

Use the systems already present rather than adding another planner layer: allow a current event/opportunity to intersect with a stored consequence, object state, habit, or spatial condition so multi-cause situations emerge. Keep chains bounded, deterministic, explainable, and sparse.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`).
