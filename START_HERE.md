# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 9: Emergent Situations and Consequence Memory**

- history: `history/2026-08-28-pixel-art-overhaul-iteration9.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration9.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration9-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration9-browser-uat.json`
- consequence evaluation: `artifacts/pixel-art-overhaul-iteration9-consequences.json`
- snapshot: `snapshots/dev/20260828T182004989725Z-pixel-art-overhaul-iteration9`
- seed/tick: **1701 / 10080**
- semantic frame SHA256: `33cced839bb3c2067da01b786c705bf5e3a2a645086e4cfdabee3748ee93f17a`
- renderer JS SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art tree SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`
- authored assets: **83**
- behavior rules: `terrarium-rules-v9-consequence-memory`
- consequence memory: `terrarium.consequence-memory.v1`, max **12** unresolved hot entries
- seasonal schema: `terrarium.seasons.v1`
- object affordances: `terrarium.object-affordances.v1`
- habits: `terrarium.habits.v1`
- situational events: `terrarium.situational-events.v1`
- spatial schema: `terrarium.spatial.v1`

Iteration 9 adds delayed causal memory without a planner. Prior event aftermath, path traces, arrangements, object displacement/state, and nesting can become later opportunities. The full append-only event ledger remains authoritative history; only a small unresolved causal index is kept hot. Recognition, approach, engagement, and recovery reuse the existing bounded intent/session machinery and action vocabulary.

Read `STATUS.md`, `ART_DIRECTION.md`, `VISUAL_STYLE_OVERHAUL.md`, `ROADMAP.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Native visual inspection

ChatGPT has verified pixel-level sight into the existing Optiplex Playwright browser. Use `Optiplex_MCP` for browser actions/state, then call `browser_screenshot` with **no filename**, `full_page=false`, PNG, and CSS scale whenever art quality, composition, clipping, sprite appearance, layout, or other rendered-pixel facts matter. A saved screenshot path is not equivalent evidence that the model saw the pixels. Single screenshots support frame-level judgment; temporal smoothness still requires repeated/time-separated evidence.

## Authority contracts

- semantic/reference frame: **800×480**; pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, habits, event occurrence/lifecycle, attention, temporary affordances, routes/contact, object identity/state, **consequence memory/opportunity selection**, history, time, and pacing;
- renderer may visualize authoritative consequence-linked actions but may not invent a consequence, remember one privately, select a revisit, or add narrative markers;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry remains `terrarium.spatial.v1`.

## Current causal law

Situational events remain **event → perception/attention → reaction/defer → engagement → aftermath**. Stateful objects remain **identity/state → available affordance → contact/action → persistent state transition → later possibility**. Iteration 9 adds **prior cause → compact unresolved consequence → delayed recognition → ordinary approach/re-engagement → bounded recovery**.

Equivalent immediate visible states may now legitimately produce different later futures when their canonical causal histories differ. Each history must remain individually deterministic and exact-replayable. Migration of old worlds starts with empty consequence memory; never backfill fictional consequences by scanning old history.

Keep using **attention + affordances + persistent state + habits + bounded causal commitments + bounded consequence memory**. Do not infer GOAP, quests, needs/personality stats, dialogue, inventory UI, or LLM action selection.

## Accepted visual grammar

The accepted 8B room, 8C Moss vocabulary, 8D object-state variants, 8E atmosphere, and 8F seasons remain intact. Iteration 9 required no renderer subsystem change: `react`, authored `walk`, and quiet `inspect`/`loaf`/`rest`/`look_outside` poses carry causal meaning from canonical event details. Renderer-local consequence memory is prohibited.

## Planned next iteration

**Iteration 10 — Causal Composition and Situation Chaining.** Let current canonical events/opportunities intersect with stored consequences, object state, habits, and spatial context so multiple existing systems can produce richer unscripted situations. Prefer composition over more memory, more verbs, or a generic planner.

## Interposed presentation boundary

Before Iteration 10 begins, finish the staged Godot cutover. Explicit cutover approval has already been given, but normal delivery is now **Godot Web in a browser**, not a required native Godot installation on each client. Source is prepared for a single-threaded Web export plus a presentation-only HTTPS gateway; generated `display/web/godot/` and extended browser live UAT are still pending. Current evidence: `artifacts/godot-art-gate/web-cutover/readiness.json`. Canvas remains immediate same-world rollback. Do not move simulation authority into the browser/gateway and do not begin Iteration 10 until the browser canary passes or is deliberately deferred.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, Python-3.10 grammar parsing, technical/behavior/spatial/coherence/habit/repertoire/situational/object-affordance/atmosphere/season/**consequence** evaluators, exact replay, deterministic temporal capture, and real 800×480 browser inspection. Major behavior changes retain seeds **1701 / 1702 / 42 / 999** at **10,080** steps. Explicitly test history-sensitive divergence and individual determinism.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific product work stays in Terrarium unless evidence demonstrates a reusable substrate deficiency.
