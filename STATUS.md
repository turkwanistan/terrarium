# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 7: Situational Events and Environmental Attention**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration7.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration7.json`
- situational-event evaluation: `artifacts/pixel-art-overhaul-iteration7-situations.json`
- repertoire regression: `artifacts/pixel-art-overhaul-iteration7-repertoire.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration7-regression-matrix.json`
- real-renderer UAT: `artifacts/pixel-art-overhaul-iteration7-browser-uat.json`
- accepted snapshot: `20260828T010131008922Z-pixel-art-overhaul-iteration7`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `c9b3e44af04bfba888d335add0bce822ffc59968029cbd13b8cbbee22c5e0fe2`
- behavior rules: `terrarium-rules-v6-situational-attention`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- short-horizon context: `terrarium.behavior-context.v1`
- long-horizon habits: `terrarium.habits.v1`
- affordance history: `terrarium.affordances.v1`
- spatial schema: `terrarium.spatial.v1`

## What Iteration 7 established

The world can now initiate bounded, canonical situations rather than relying on Moss to originate nearly every visible activity. The initial event catalog is deliberately small: **moving sunlight, bird outside, rain intensification, thunder, night moth, and leaf/window contact**. Each event has deterministic occurrence conditions, authoritative lifecycle/duration, salience/perceptibility, source location, and any temporary affordance it creates.

Moss does not treat events as mandatory interrupts. Depending on current commitment, event salience, recent repetition, and deterministic attention choice, Moss may **ignore, orient briefly, defer, rarely interrupt a low-commitment activity, approach, engage, or recover into ordinary behavior**. Existing object sessions, possession continuity, supported sleep, learned habits, and calm activity commitments remain authoritative. The target causal shape is now real state rather than renderer theater: **event → perception/attention → reaction or defer → engagement/decision → aftermath**.

Moving sunlight is the first temporary environmental affordance. Its current patch is authoritative world state, Moss can travel to that exact walkable location and loaf there, and the opportunity moves/disappears with the event. Window events keep separate source coordinates and physically valid Moss engagement anchors: the renderer shows where the bird/thunder/leaf/rain event exists while navigation still ends on valid floor-side geometry.

## Acceptance evidence

Across deterministic seven-day runs for seeds **1701 / 1702 / 42 / 999**:

- **51–63** situational events start per seed;
- every seed reaches all six event types;
- event-active timeline share is only **6.7–8.5%**;
- event-linked decisions are only **6.3–8.8%** of decisions, leaving >91% ordinary autonomous behavior on every seed;
- ignored, oriented, deferred, and engaged responses all occur across the matrix;
- same-type event starts are separated by at least **115 world-minutes**;
- true interruptions are rare: only three across the four final runs, limited to `rest` / `loaf`; high-commitment manipulation and sleep are not casually broken;
- sunlight temporary-affordance use occurs on every seed with **zero invalid-affordance failures**;
- causal engagement checks report **zero mismatches**.

Iteration-6 repertoire breadth is preserved rather than crowded out. Final family entropy is **2.960–2.999 bits**, generic behavior share is **56.6–59.4%**, and the original repertoire evaluator passes all four seeds. Controlled equivalent-present-state histories still diverge deterministically: loaf-pattern cross-advantage is **0.237** and placement-pattern cross-advantage is **0.250**, both above the unchanged Iteration-6 acceptance bars. The arrangement preference strength was deliberately tuned to preserve this history dependence while retaining the original `<70%` anti-lock-in probe.

Long-horizon habits also remain causal and bounded. All four habit robustness seeds pass; controlled favorite-zone cross-advantage remains **0.238–0.361**. Coherence remains calm: ordinary non-delivery reversal is **0–2.33%**, and the calm visible timeline is **68.3–76.1%** across the four reference runs.

## Renderer / browser UAT

The actual Canvas renderer consumes canonical `world_event` state. Sunlight is a hard-edged finite-palette rug patch; bird, rain escalation, thunder, and leaf contact remain localized to the window; the moth is a small night event near the activity corner. There is no renderer-owned event scheduling, hidden preference memory, camera shake, random zoom, full-screen particle layer, or high-resolution overlay.

Real 800×480 browser UAT covered **sunlight engagement, bird engagement, thunder reaction, moth engagement, and deliberate event non-reaction**. Every scenario captured **11 temporal samples**, all with exact 400×240→800×480 2× scaling, smoothing disabled, and monotonic interpolation. Each scenario produced **8–10 distinct raster states**. Browser runs reached the ready state with zero console errors. Human inspection of the actual Canvas output found the event cues restrained, pixel-native, localized, and subordinate to Moss.

Canonical Moss was not reset, replaced, or used for development fixture UAT. Browser evaluation used an isolated temporary world; the service was stopped afterward.

## Validation

- pytest: **43/43 PASS**;
- Python 3.10 grammar parse: **24 source files PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator / exact replay / restart / hash-chain integrity: **PASS**;
- behavior robustness, seeds 1701/1702/42/999: **all PASS**;
- spatial robustness, seeds 1701/1702/42/999: **all PASS**;
- coherence robustness, seeds 1701/1702/42/999: **all PASS**;
- long-horizon habit robustness, seeds 1701/1702/42/999: **all PASS**;
- Iteration-6 repertoire regression, seeds 1701/1702/42/999: **all PASS**;
- Iteration-7 situational-event evaluation, seeds 1701/1702/42/999: **all PASS**;
- real browser Iteration-7 temporal UAT: **PASS**;
- combined Iteration-7 regression matrix: **PASS**.

## SBC conclusion

No reusable substrate deficiency was exposed. Canonical environmental-event state, selective attention, deferral/interruption policy, temporary affordances, causal evaluation, replay, migration, and renderer support all fit cleanly inside Terrarium's existing bounded-session model and the already-promoted SBC/project/evaluation substrate. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18 decision: NO — existing SBC substrate remains sufficient.**

## Roadmap after Iteration 7

1. **Iteration 8 — Object Identity and Stateful Affordances:** object classes gain materially different affordance subsets and persistent state transitions so props stop feeling like skins for one generic interaction graph.
2. **Iteration 9 — Emergent Situations and Consequence Memory:** environmental events, object state, arrangements, and learned habits compose into later opportunities over minutes/hours/days without scripted quest chains.

Iteration 7 deliberately does not introduce GOAP, a generic planner, needs/personality-stat systems, quest logic, dialogue systems, or LLM action selection. Revisit planning/SBC substrate only if later product evidence shows that attention + affordances + persistent state + habits + short causal commitments cannot express the required situations cleanly.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Any host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
