# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 6: Behavioral Repertoire and World Affordances**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration6.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration6.json`
- multi-seed repertoire evaluation: `artifacts/pixel-art-overhaul-iteration6-evaluation.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration6-regression-matrix.json`
- real-renderer UAT: `artifacts/pixel-art-overhaul-iteration6-renderer-uat.json`
- accepted snapshot: `20260827T233841118223Z-pixel-art-overhaul-iteration6`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `0a759f58fa022f3dcbf7dd4de33c632bb9ee9366b82e0b077d71eacd6314102e`
- renderer JS SHA256: `66a80f9e86d3242a2c99903956faa39873dd7dbfc0233869af8c2952bb56cd19`
- behavior rules: `terrarium-rules-v5-behavioral-repertoire`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- short-horizon context: `terrarium.behavior-context.v1`
- long-horizon habit profile: `terrarium.habits.v1`
- affordance history: `terrarium.affordances.v1`
- spatial schema: `terrarium.spatial.v1`

## What Iteration 6 established

Iteration 5 had ten decision labels but only seven meaningfully different semantic activity families; travel, idle/rest, and one inspect→carry→place object loop still dominated what a viewer could actually see. Iteration 6 expands the reachable life-space without adding a planner, needs system, personality stats, dialogue logic, or LLM decision-making.

Moss can now **nudge** placed objects authoritatively and remain to inspect the result; **loaf**, **groom**, and **stretch** as distinct calm activities; react to deterministic rain/mist and carry that reaction through to a window session; and arrange carried objects across plausible personal spaces rather than treating the collection shelf as the universal destination. `terrarium.affordances.v1` records only real post-upgrade activity: semantic family completions, object nudges, zone comfort, and zone arrangements. Existing worlds migrate neutrally and no pre-Iteration-6 affordance history is fabricated.

The weather cycle was also corrected: the previous arithmetic generator made canonical seed 1701 effectively clear forever. Weather is now deterministic per three-hour world block but actually varies across clear/rain/mist, giving environmental reactions a real causal opportunity while remaining independent of action RNG.

## Acceptance evidence

The Iteration-5 baseline has **7 meaningful families**, family entropy **2.663–2.697 bits**, and generic idle/rest/travel/sleep behavior at **71.2–73.5%** of decisions. Across seeds **1701 / 1702 / 42 / 999**, Iteration 6 reaches **all 10 meaningful families**. Family entropy rises to **2.915–2.946 bits**, generic share falls to **58.2–60.5%**, and no family exceeds **23.5%** of decisions. Every seed reaches **40–41 zone×family combinations**, **63–66 distinct family transitions**, all six objects are nudged, and arrangement/comfort history reaches all five zones.

New activities remain bounded rather than taking over: `loaf + groom + stretch + nudge + react` account for roughly **11.8–13.7%** of decisions. Inspect sessions lead to manipulation within two decisions **72.9–76.5%** of the time. Nudge→same-object re-inspection succeeds **91.3–100%** of the time, and weather reaction→window follow-through succeeds **94.1–100%**.

Equivalent-present-state controlled histories remain exactly deterministic individually but now diverge through the new affordance space. A window/amber-leaf history versus activity-corner/acorn history produces **0.280 loaf-pattern cross-advantage** and **0.341 placement-pattern cross-advantage**, with different final authoritative object arrangements after 3,000 ticks.

## Renderer / pacing / persistence

The actual 800×480 Canvas renderer has authored poses for nudge, loaf, groom, stretch, and react. Browser temporal UAT sampled 11 frames per new scenario with exact 400×240→800×480 2× scaling and smoothing disabled. Each activity produced **5–8 distinct raster states**. Nudge visibly holds paw contact before displacement, then moves monotonically at ~3.7% → 43.7% → 91.1% and settles by **1.7 s**, rather than teleporting the object.

Iteration-4 pacing remains intact. In the final reference coherence run, purposeful movement is **100%**, window-session continuation **100%**, wake recovery **100%**, post-place linger **100%**, and the calm visible timeline is **74.6%**. Existing habits remain bounded and all four robustness seeds pass the original long-horizon habit evaluator.

Persistence remains event-authoritative: exact snapshot+event replay, restart preservation, append-only hash-chain integrity, valid spatial endpoints, and blocker avoidance all pass. Canonical Moss was not reset or replaced during development or UAT.

## Validation

- pytest: **39/39 PASS**;
- Python 3.10 grammar parse: **30 source files PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **PASS**;
- behavior evaluator: **PASS**;
- spatial evaluator: **PASS**;
- Iteration-4 coherence robustness, seeds 1701/1702/42/999: **all PASS**;
- Iteration-5 long-horizon habit robustness, seeds 1701/1702/42/999: **all PASS**;
- Iteration-6 repertoire evaluation, seeds 1701/1702/42/999: **all PASS**;
- real browser Iteration-6 temporal UAT: **PASS**;
- combined Iteration-6 regression matrix: **PASS**.

## SBC conclusion

No reusable substrate deficiency was exposed. The new affordance state, causal activity chains, renderer poses, long-run variety evaluation, migration, and history-divergence evidence are Terrarium product concerns and fit the existing SBC/project/evaluation/temporal substrate. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18 decision: NO — existing SBC substrate remains sufficient.**

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Any host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or the explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
