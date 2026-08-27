# Pixel-Art Overhaul — Iteration 6: Behavioral Repertoire and World Affordances

**Date:** 2026-08-27
**Status:** ACCEPTED product checkpoint
**Snapshot:** `20260827T233841118223Z-pixel-art-overhaul-iteration6`
**Seed/tick:** `1701 / 10080`
**Semantic frame SHA256:** `0a759f58fa022f3dcbf7dd4de33c632bb9ee9366b82e0b077d71eacd6314102e`
**Renderer JS SHA256:** `66a80f9e86d3242a2c99903956faa39873dd7dbfc0233869af8c2952bb56cd19`

## Weaknesses actually found

Iteration 5 made Moss history-dependent, but its reachable life was still narrow. The engine exposed ten decision labels, yet semantic grouping reduced them to only **seven meaningfully different families**: `travel`, `idle`, `comfort`, `investigate`, `arrange`, `observe`, and `sleep`. `explore` was still visually locomotion, `idle/rest` occupied similar quiet space, and almost all object life converged on inspect→carry→place. Across the four Iteration-5 seven-day baselines, generic idle/rest/travel/sleep behavior consumed **71.2–73.5%** of decisions and family entropy was only **2.663–2.697 bits**.

The audit also found that canonical seed 1701's old weather arithmetic produced effectively clear weather forever, so weather existed in frame state but did not create a meaningful environmental opportunity for canonical Moss.

## Change — affordances, not animation count

Added a bounded repertoire expansion under `terrarium-rules-v5-behavioral-repertoire` while preserving the accepted `terrarium-rules-v3-routine-coherence` RNG stream.

- **Object manipulation / play:** `nudge` approaches and contacts a placed object, changes its authoritative authored-slot position, increments persistent nudge/move history, and establishes a causal re-inspection continuation.
- **Comfort / self-directed life:** `loaf`, `groom`, and `stretch` use distinct commitments and authored poses rather than aliases for generic idle. Loaf probability may be gently shaped by the existing learned zone habit.
- **Personal-space arrangement:** object pickup chooses among plausible authored destinations instead of treating the shelf as the universal sink. Existing zone/context/object affinity may bias the choice while leaving substantial exploration floors.
- **Environmental reaction:** rain/mist can produce `react → travel to window → look_outside`. Weather is deterministic from seed + world-time block but now actually varies across clear/rain/mist.
- **Persistent affordance history:** additive `terrarium.affordances.v1` records completed semantic families, per-object nudges, zone comfort use, and zone arrangements. Existing worlds migrate to empty/neutral affordance history; no old activity is invented.

No GOAP, general planner, LLM decision-making, personality scores, hunger/happiness meters, schedules, dialogue, or arbitrary drive system was introduced.

## Causal activity composition

New actions are deliberately chained where consequence matters. Inspect may lead to either carry/arrange or nudge/play. Nudge then strongly preserves the object-centered session until Moss regards the displaced object. A weather reaction preserves its causal destination until the window session begins. Wake recovery was also tightened during regression work so new activity choices could not erode the accepted recovery-before-travel invariant.

The renderer gained explicit pixel-native `nudge`, `loaf`, `groom`, `stretch`, and `react` poses. Nudge has separate paw-contact and displacement phases; the object remains stationary during contact and slides only after contact has visually registered.

## Long-horizon variety evidence

All four 10,080-tick runs pass `evaluate_repertoire.py`:

| Seed | Families | Entropy | Generic share | New-action share | Zone×family | Family transitions | Nudges | Nudge→reinspect | Weather→window |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1701 | 10 | 2.931 | 59.85% | 13.72% | 40 | 66 | 55 | 100.0% | 94.1% |
| 1702 | 10 | 2.942 | 59.11% | 11.80% | 41 | 63 | 59 | 94.9% | 100.0% |
| 42 | 10 | 2.946 | 60.46% | 12.45% | 41 | 66 | 69 | 91.3% | 100.0% |
| 999 | 10 | 2.915 | 58.20% | 12.57% | 40 | 63 | 63 | 98.4% | 100.0% |

Every seed uses all old actions, all ten semantic families, all five comfort-history zones, all five arrangement-history zones, and all six objects as nudge targets. No semantic family exceeds **23.5%** of decisions. Each run produces **30 distinct arrangement patterns** and **54–65 distinct nudge patterns**.

## History-dependent divergence

The controlled experiment starts physically equivalent same-seed worlds with different mature histories. Each history repeats exactly under duplicate execution. With a window/amber-leaf history versus an activity-corner/acorn history, the new repertoire itself diverges:

- favorite-zone loaf-pattern cross-advantage: **0.279720**;
- favorite-zone placement-pattern cross-advantage: **0.340741**;
- final authoritative object arrangements: **different**;
- neither world loses ordinary exploration or old behaviors.

This is the Iteration-6 target: history now changes not only which zone/object Moss selects, but what kinds of comfort and arrangement activity visibly accumulate there.

## Real renderer UAT

The actual 800×480 Canvas renderer was run through deterministic development fixtures for `object_nudge`, `loaf`, `groom`, `stretch`, and `weather_reaction`. Every scenario sampled 11 frames and preserved exact 400×240→800×480 2× integer scaling with smoothing off. Distinct raster states per sequence were **7 / 5 / 6 / 8 / 5** respectively.

For `object_nudge`, displacement progress was monotonic: the object remained at **0%** through the 500 ms paw-contact phase, then moved to **3.7% at 800 ms**, **43.7% at 1100 ms**, **91.1% at 1400 ms**, and **100% / settled at 1700 ms**. Browser UAT reported zero page errors for the new-affordance sequences.

## Regression evidence

Final validation after all code changes:

- **39/39 pytest PASS**;
- **30 Python source files** parse with Python 3.10 grammar;
- JavaScript syntax PASS;
- technical PASS, including exact snapshot+event replay, append-only chain, and restart preservation;
- behavior PASS;
- spatial PASS;
- coherence PASS for seeds **1701 / 1702 / 42 / 999**;
- legacy long-horizon habit evaluator PASS for seeds **1701 / 1702 / 42 / 999**;
- Iteration-6 repertoire evaluator PASS for seeds **1701 / 1702 / 42 / 999**;
- renderer UAT PASS;
- combined regression matrix PASS.

Seed 1701 / 2,000-tick coherence retains **100% purposeful movement**, **100% window continuation**, **100% wake recovery**, **100% post-place linger**, and **74.55% calm visible timeline**. Canonical Moss was never reset or replaced; browser/service UAT used disposable state only.

## SBC decision

No reusable SBC substrate gap appeared. The existing project sandbox, deterministic simulation/evaluation machinery, spatial authority, browser/temporal tooling, and promoted capabilities were sufficient. No Self-Building Computer files, Capability Forge capability, or frozen MCP tool surface changed. **Gen18 decision: NO — existing SBC substrate remains sufficient.**
