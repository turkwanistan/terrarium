# Pixel-Art Overhaul — Iteration 4: Behavioral Intent and Routine Coherence

**Date:** 2026-08-27
**Status:** ACCEPTED product checkpoint
**Snapshot:** `20260827T212849313774Z-pixel-art-overhaul-iteration4`
**Seed/tick:** `1701 / 698`

## Weaknesses actually found

The Iteration-3 engine was spatially correct but still selected many decisions independently. A 2,000-tick baseline produced 5.19 movement decisions/hour, 2.22 cross-room moves/hour, 34 movement-to-movement reversals, only 18.7% inspect→same-object-carry continuation within two decisions, 60% window-arrival→watch continuation, and 39.3% wake→quiet-recovery continuation. Concrete traces included picking up an object, resting, crossing toward one zone, immediately crossing elsewhere, then placing it there.

## Change

Added bounded `terrarium.behavior-context.v1`: four recent zones, four recent objects, and one current intent. Destination selection now inhibits recent-zone ping-pong and uses the existing authored spatial anchors as familiar places. Arrival, window, object, post-place, sleep, and wake contexts bias only the next few choices; they do not form hard-coded scripts.

Object pickup chooses a delivery destination once and completes that chain. Inspect sessions prefer the same object; completed sessions briefly inhibit the just-used object when another local object exists. Window, idle/rest, place, sleep, and wake commitments were lengthened enough to read as sessions/recovery. Legacy worlds migrate this bounded context through normal deterministic evolution, including the case where Moss is already carrying something.

No renderer authority changed. `display/web/app.js` is byte-identical to Iteration 3.

## Evidence

Seed 1701 / 2,000 ticks improved decisions/hour **22.20→17.49**, movement/hour **5.19→3.42**, cross-room movement/hour **2.22→1.26**, average dwell **10.20→15.04 ticks**, post-arrival linger **89.6%→98.2%**, inspect→same-object carry within two decisions **18.7%→83.0%**, window arrival→watch **60.0%→92.9%**, post-place linger **87.0%→100%**, and wake recovery **39.3%→100%**. All four robustness seeds (1701, 1702, 42, 999) passed the new coherence evaluator.

The real 3-second browser/dev world naturally produced: **window watch → linger → inspect amber leaf → carry amber leaf → direct collection-shelf delivery → settle/place → sleep**. Real RAF was p50/p95 16.7 ms, max 16.8 ms, no stalls; the promoted temporal auditor passed the fresh RAF evidence with zero critical failures.

Validation: **28/28 pytest PASS**, JS syntax PASS, technical PASS, behavior PASS, spatial PASS with 0 blocker intersections / 0 invalid awake endpoints, coherence PASS, deterministic duplicate equality PASS, exact replay/restart PASS.

## SBC decision

No reusable SBC substrate gap appeared. The new measurement is specifically a Terrarium behavior-quality property and belongs in Terrarium. Existing promoted temporal capability remained sufficient. No SBC files, MCP surface, Capability Forge capability, or Gen18 work was added.
