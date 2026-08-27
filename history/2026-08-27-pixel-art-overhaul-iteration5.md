# Pixel-Art Overhaul — Iteration 5: Long-Horizon Preferences and Habit Formation

**Date:** 2026-08-27
**Status:** ACCEPTED product checkpoint
**Snapshot:** `20260827T222822886488Z-pixel-art-overhaul-iteration5`
**Seed/tick:** `1701 / 10080`

## Weaknesses actually found

Iteration 4 made the next action make sense, but a seven-day baseline still had no persistent preference state. Long-run object attention stayed close to uniform: the strongest object share was only **18.4–20.2%** across seeds 1701/1702/42/999. The engine also applied an ever-growing `times_inspected` novelty penalty, so repeated positive use was eventually suppressed rather than becoming a durable preference. Zone use varied naturally, but different histories could not persistently bias future choices once the immediate routine context matched.

## Change

Added compact canonical `terrarium.habits.v1` state: bounded zone affinity, per-object affinity, and zone affinity conditioned on the existing dawn/day/dusk/night lighting phases. There are no personality labels, needs bars, schedules, dialogue, planners, or LLM semantics. Preferences are learned only from ordinary persisted behavior.

Reinforcement is slow and saturating; every qualifying experience also applies slight global decay. Preference influence is mean-normalized, bounded, and phased in only after substantial experience. Existing recent-zone/recent-object inhibition remains authoritative for short-horizon repetition control. Object lifetime novelty pressure is now capped so it cannot mathematically erase long-term preference, while immediate recently-used-object inhibition still prevents loops.

Existing Iteration-4 worlds migrate conservatively to a neutral `terrarium.habits.v1` baseline on their next ordinary canonical transition. Existing creature/object state, possessions, routine context, and event history are preserved. We deliberately do not pretend that old events can be reconstructed into exact preferences under rules that did not exist when those events occurred.

The behavior rules are now `terrarium-rules-v4-long-horizon-habits`, while the deterministic action RNG stream intentionally remains pinned to the accepted Iteration-4 stream so upgrading the model does not gratuitously reroll Moss before habits mature.

## Evidence

All four seven-day / 10,080-tick runs pass the long-horizon evaluator. Final learned zone-affinity ranges are **0.149–0.238** and object-affinity ranges **0.099–0.194**. Yet the strongest autonomous non-delivery destination remains only **24.0–25.2%** of choices and the strongest selected object only **19.0–20.7%**, with all five zones and all ten action classes still used.

A causal controlled-opportunity probe neutralizes only the learned profile while holding physical opportunity and deterministic random draws constant. Learned favorite-zone preference increases its choice probability by **+2.25 to +4.29 percentage points** across the four seeds; learned favorite-object preference increases choice probability by **+1.96 to +3.58 points**.

The explicit history-divergence experiment starts two worlds with identical present physical state and the same seed but different mature accumulated preferences. A window/amber-leaf history and an activity-corner/acorn history remain individually deterministic, continue exploring every zone, and produce a **0.177–0.324** combined favorite-zone cross-advantage across seeds. Their favorite-zone shares remain tendencies, not schedules.

Seed 1701 retains Iteration-4 short-horizon quality at 2,000 ticks: purposeful movement **100%**, direct delivery **100%**, post-arrival linger **98.2%**, inspect→same-object carry **80.0%**, window-session continuation **90.9%**, post-place linger **100%**, wake recovery **100%**, average dwell **14.93 ticks**, and recent-object repeat after place **0%**.

Real 800×480 browser UAT used deterministic day-2/day-5/day-7 habit fixtures through the actual Canvas renderer. All loaded `Temporal ready`; the day-7 raster retained exact 400×240→800×480 integer scaling with smoothing off and `scale2x_error_blocks=0` (`fnv1a32:d50a941d`). The accepted renderer JS is byte-identical to Iteration 4.

An intentionally extreme disposable 0.01-second accelerated development service exposed a shared-store event-extension race at tick 623 while the debug endpoint was reading. It was not used as acceptance evidence, does not occur in the normal three-second product cadence, and does not justify broadening this iteration into a persistence-concurrency rewrite.

Validation: **33/33 pytest PASS**, Python-3.10 grammar guard PASS, JavaScript syntax PASS, technical PASS with exact replay/restart, behavior PASS, spatial PASS with **0 blocker intersections / 0 invalid awake endpoints**, Iteration-4 coherence PASS for all four robustness seeds, and Iteration-5 long-horizon evaluation PASS for all four robustness seeds.

## SBC decision

No reusable SBC substrate gap appeared. Persistent preference learning, migration, history-divergence evaluation, and browser habit observation are Terrarium product concerns and fit existing project/evaluation/temporal capabilities. Self-Building Computer and the frozen Optiplex MCP surface were not modified. **Gen18 is not warranted.**
