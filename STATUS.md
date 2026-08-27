# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 5: Long-Horizon Preferences and Habit Formation**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration5.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration5.json`
- long-horizon evaluation: `artifacts/pixel-art-overhaul-iteration5-evaluation.json`
- accepted snapshot: `20260827T222822886488Z-pixel-art-overhaul-iteration5`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `a275783dc04234b1da10d8bb6dd1b8a2bcaaeba134ee5ae07f0062687cf51290`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- behavior rules: `terrarium-rules-v4-long-horizon-habits`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- short-horizon context: `terrarium.behavior-context.v1`
- long-horizon habit profile: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

## What Iteration 5 established

Moss now accumulates a deliberately small persistent preference profile from lived experience: zone affinity, object affinity, and zone affinity conditioned on dawn/day/dusk/night. Preference is not a needs system, personality score, schedule, dialogue layer, quest system, planner, or LLM interpretation. It changes future weighted choices only after substantial experience.

Reinforcement is saturating and accompanied by slight decay. Choice influence is normalized against competing affinities, bounded, phased in slowly, and retains exploration floors. Iteration-4 recent-zone/recent-object inhibition remains active, so long-horizon familiarity cannot override immediate anti-repetition behavior. Lifetime object novelty pressure is capped so it no longer makes durable favorites mathematically impossible.

Existing worlds migrate conservatively to a neutral habit profile on their next ordinary transition while preserving Moss, current possessions, object positions/counts, short-horizon routine context, and the append-only historical ledger. The system does not fabricate exact preferences from pre-Iteration-5 history.

## Acceptance evidence

Across seeds **1701 / 1702 / 42 / 999**, seven-day 10,080-tick habit evaluation is **PASS**. Learned zone-affinity ranges are **0.149–0.238** and object-affinity ranges **0.099–0.194**. The top autonomous non-delivery destination remains only **24.0–25.2%** and the top selected object **19.0–20.7%**; every seed still uses all five zones and all ten action classes.

Controlled opportunity probes show the learned profile itself causes future selection change: learned favorite-zone uplift **+2.25 to +4.29 percentage points**, learned favorite-object uplift **+1.96 to +3.58 points**. Equivalent-present-state worlds with different mature histories remain deterministic individually but diverge in future tendencies, with combined favorite-zone cross-advantage **0.177–0.324**.

Seed 1701 / 2,000 ticks retains accepted short-horizon coherence: purposeful movement **100%**, direct delivery **100%**, post-arrival linger **98.2%**, inspect→same-object carry **80.0%**, window continuation **90.9%**, post-place linger **100%**, wake recovery **100%**, and average dwell **14.93 ticks**.

Real 800×480 Canvas UAT rendered deterministic day-2/day-5/day-7 habit checkpoints. All were `Temporal ready`; day 7 retained exact 400×240→800×480 integer scaling with smoothing disabled and zero 2× scale errors. The renderer source is byte-identical to Iteration 4.

## Validation

- pytest: **33/33 PASS**;
- Python 3.10 grammar guard: **PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **PASS**, including append-only hash chain, restart persistence, and exact snapshot+event replay;
- behavior evaluator seed 1701 / 2000: **PASS**, all 10 action classes;
- spatial evaluator seed 1701 / 2000: **PASS**, **0 blocker intersections**, **0 invalid awake endpoints**;
- Iteration-4 coherence robustness: **1701 / 1702 / 42 / 999 all PASS**;
- Iteration-5 long-horizon robustness: **1701 / 1702 / 42 / 999 all PASS**;
- temporal rendering tests: **6/6 PASS**;
- browser integer-scale telemetry: **PASS**.

An intentionally extreme disposable 0.01-second development service exposed a shared-store event-extension race under concurrent debug access at tick 623. It was stopped, excluded from acceptance evidence, never touched canonical Moss, and does not justify changing the normal three-second product runtime or SBC substrate within this iteration.

## Pixel-art / pacing invariants

`ART_DIRECTION.md` remains visual authority. Internal art stays **400×240**, presented as exact **2× nearest-neighbor 800×480** with smoothing off. The product heartbeat remains **3 real seconds**, world advance **1 minute/heartbeat**, full day ~**72 real minutes**. Host state owns behavior/preferences/routes; the renderer only shows their consequences.

## SBC conclusion

No reusable substrate deficiency was exposed. `terrarium.habits.v1`, migration, history-divergence evaluation, and habit UAT are product-specific Terrarium work using existing promoted capabilities. No SBC files, Capability Forge capability, or frozen MCP surface changed. **Gen18 is not warranted.**

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. The mediated project boundary cannot inspect or restart the actual user-owned OptiPlex Moss process; deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or the explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
