# Pixel-Art Overhaul — Iteration 7: Situational Events and Environmental Attention

**Date:** 2026-08-27  
**Status:** ACCEPTED product checkpoint  
**Snapshot:** `20260828T010131008922Z-pixel-art-overhaul-iteration7`  
**Seed/tick:** `1701 / 10080`  
**Semantic frame SHA256:** `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`  
**Renderer JS SHA256:** `c9b3e44af04bfba888d335add0bce822ffc59968029cbd13b8cbbee22c5e0fe2`

## Product weakness addressed

Iteration 6 gave Moss a broader behavioral repertoire, but the room still depended too heavily on Moss as the source of visible activity. Weather existed and could cause a reaction, yet most moments still began with Moss sampling what to do next. That limited the number of genuinely different situations the same action vocabulary could express.

Iteration 7 makes the world itself present bounded opportunities and interruptions while keeping Moss selective rather than reactive-by-default. The target shape is now explicit canonical causality:

> **event → perception/attention → reaction or defer → engagement/decision → aftermath**

This remains a normal Terrarium product iteration. No general planner, event-bus framework, needs/personality system, quest engine, dialogue system, or LLM action selector was introduced.

## Canonical situational layer

Added additive `terrarium.situational-events.v1` state and advanced behavior rules to `terrarium-rules-v6-situational-attention`.

The initial authored catalog is deliberately small:

- `sunlight` — a moving warm patch in open space that temporarily affords loafing;
- `bird` — a bounded outside-window visitor that can draw observation;
- `rain_intensify` — a temporary escalation of an already rainy window state;
- `thunder` — a salient but brief window event that may earn orientation/attention;
- `moth` — a small night event near the activity corner;
- `leaf_tap` — brief contact/noise at the window.

Each active event carries authoritative identity/type, lifecycle timing, source location, salience/perceptibility, and its engagement target/temporary affordance when applicable. Existing worlds migrate additively without replacing Moss, possessions, habits, affordance history, routine context, object state, or event ledger history.

Occurrence is deterministic and decoupled from renderer state. Per-type cooldowns prevent visible clustering without globally suppressing event variety. Same-type starts in the accepted four-seed seven-day matrix are separated by at least 115 world-minutes.

## Selective attention, not mandatory interruption

Situations are opportunities rather than commands. Moss can:

- ignore an event;
- orient briefly;
- defer while finishing a commitment;
- rarely interrupt a low-commitment activity;
- approach a physically valid engagement position;
- engage using existing action vocabulary;
- recover back into ordinary autonomous behavior.

Object manipulation, possession continuity, sleep support, spatial authority, habits, recent-history inhibition, and ordinary commitments remain stronger constraints than most event salience. True interruption is intentionally rare. Across all four final seven-day runs there are only three true interruptions, limited to `rest` / `loaf`; no high-commitment object manipulation or supported sleep is casually cancelled.

The same action can now have different causal meaning without multiplying enums. `look_outside` may be casual, rain-driven, or bird-driven; `react` may represent weather, thunder, moth, or another attention shift. Evaluators were updated to classify these by causal metadata rather than assuming every `react` is a weather reaction.

## Temporary affordance: moving sunlight

Moving sunlight is the first event-created temporary affordance. The patch's current coordinate is canonical, walkable world state rather than a renderer invention. Moss may travel to the patch and loaf there while it exists. The patch may shift once and Moss can follow that authoritative location; when it moves/expires, the previous opportunity is no longer valid.

This required the spatial evaluator to recognize valid dynamic affordance endpoints while continuing to reject arbitrary non-anchor travel. Across the accepted matrix, every seed uses sunlight affordances and there are zero invalid-affordance failures.

## Repetition and ordinary-life preservation

The event ecology was tuned against an Iteration-6 baseline rather than by action-count aesthetics. Across seeds `1701 / 1702 / 42 / 999` over 10,080 ticks each:

- events started: **63 / 53 / 62 / 51**;
- all six event types occur on every seed;
- event-active timeline share: **8.48% / 6.74% / 8.43% / 7.11%**;
- event-linked decision share: **8.79% / 6.33% / 8.04% / 7.26%**;
- ordinary autonomous decisions remain above **91%** on every seed;
- outcomes include ignored, oriented, deferred, and engaged paths rather than one mandatory response;
- causal engagement mismatches: **0**;
- sunlight affordance failures: **0**.

Iteration-6 repertoire remains intact. The original repertoire evaluator passes all four seeds on the new engine. Family entropy is **2.960–2.999 bits**, generic behavior share is **56.6–59.4%**, and the new-action share remains bounded at roughly **13.1–15.1%**.

Controlled equivalent-present-state histories still diverge deterministically. Final cross-advantages are **0.237** for loaf patterns and **0.250** for placement patterns, both above the unchanged Iteration-6 thresholds. During acceptance tuning, arrangement habit strength was reduced to the narrow point that preserves this divergence while also preserving the original `<70%` anti-lock-in probe; the final controlled activity-corner destination share is **69.75%**.

## Existing habit/coherence preservation

Long-horizon habit evaluation remains green on all four robustness seeds. Controlled favorite-zone history cross-advantage is **0.361 / 0.238 / 0.244 / 0.286** for seeds 1701/1702/42/999.

Event-driven travel is classified separately from ordinary autonomous travel in coherence evaluation so a legitimate event response is not mislabeled as random ping-pong. Ordinary recent-zone inhibition was also tightened slightly after seed 42 exposed a small real backtracking excess. Final ordinary non-delivery reversal rates are **0% / 0% / 0% / 2.33%**, with calm visible timeline ratios **68.3% / 76.1% / 74.25% / 73.05%**.

## Renderer and actual-browser UAT

The renderer remains subordinate to canonical state and preserves the accepted 400×240 pixel-native art surface with exact 2× nearest-neighbor presentation.

Authored environmental cues:

- sunlight: hard-edged finite-palette rug patch;
- bird: small localized window silhouette;
- rain intensification: denser but still bounded pane rain;
- thunder: localized window cue rather than full-room flash/shake;
- moth: tiny night movement near the activity corner;
- leaf tap: brief pane-local contact cue.

No `Math.random`, renderer-owned event scheduling, high-resolution overlay, random jitter, camera shake, random zoom, bloom, or full-scene event effects were introduced.

Real-browser temporal UAT on the final fixture pack covered:

1. `event_sunlight_engage`;
2. `event_bird_engage`;
3. `event_thunder_react`;
4. `event_moth_engage`;
5. `event_ignored`.

Each scenario captured **11 samples**. All samples preserve exact 400×240→800×480 scaling, smoothing off, and monotonic interpolation. Each scenario produces **8–10 distinct raster states**. Browser runs reached `ready` with zero console errors. Human visual inspection found the cues restrained, pixel-native, localized, and subordinate to Moss.

UAT used an isolated temporary development world and deterministic fixtures. Canonical Moss was never reset or replaced; the isolated service was stopped afterward.

## Validation

- pytest: **43/43 PASS**;
- Python 3.10 grammar parse: **24 source files PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator / restart / exact replay / append-only hash chain: **PASS**;
- behavior, seeds 1701/1702/42/999: **all PASS**;
- spatial, seeds 1701/1702/42/999: **all PASS**;
- coherence, seeds 1701/1702/42/999: **all PASS**;
- habits, seeds 1701/1702/42/999: **all PASS**;
- Iteration-6 repertoire regression, seeds 1701/1702/42/999: **all PASS**;
- Iteration-7 situational-event evaluation, seeds 1701/1702/42/999: **all PASS**;
- final actual-browser temporal UAT: **PASS**;
- combined Iteration-7 regression matrix: **PASS**.

Primary evidence:

- `artifacts/pixel-art-overhaul-iteration7.json`;
- `artifacts/pixel-art-overhaul-iteration7-situations.json`;
- `artifacts/pixel-art-overhaul-iteration7-repertoire.json`;
- `artifacts/pixel-art-overhaul-iteration7-browser-uat.json`;
- `artifacts/pixel-art-overhaul-iteration7-regression-matrix.json`;
- multi-seed behavior/spatial/coherence/habit artifacts under `artifacts/pixel-art-overhaul-iteration7-*`.

## SBC / Gen18 decision

**NO Gen18.** No reusable SBC substrate deficiency was exposed. Canonical events, selective attention, deferral/interruption semantics, temporary affordances, persistence/replay, deterministic evaluation, and pixel-renderer consumption all fit cleanly inside Terrarium's existing bounded-session architecture and existing promoted SBC capabilities. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

## Next product iteration

**Iteration 8 — Object Identity and Stateful Affordances.**

Now that the world can present causes and Moss can selectively attend to them, the next highest-value expansion is to make object identity materially change what can happen. Different object classes should expose different affordance subsets and persistent state transitions rather than all collapsing into the same inspect/carry/place graph. Iteration 9 can then compose event state, differentiated object state, arrangements, and habits into longer emergent situations.
