# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 8D: Object Identity and Stateful Affordances**

- history: `history/2026-08-28-pixel-art-overhaul-iteration8d.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8d.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8d-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8d-browser-uat.json`
- object-affordance evaluation: `artifacts/pixel-art-overhaul-iteration8d-object-affordances.json`
- art-direction matrix: `artifacts/iteration8d-art-direction-matrix.json`
- snapshot: `snapshots/dev/20260828T112207258140Z-pixel-art-overhaul-iteration8d`
- seed/tick: **1701 / 10080**
- semantic frame SHA256: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`
- renderer JS SHA256: `f8e12181a18c2616fdeb8dae1ee5a0453fab6ba3a5ab88912782e497e35cb701`
- authored-art tree SHA256: `ed1fee4cd060519267d131837ab45772754108c1c2eaa4c9a9c65322bce08d9a`
- authored asset count: **73** (**46 Moss / 13 object-state assets**)
- behavior rules: `terrarium-rules-v7-object-identity`
- object affordances: `terrarium.object-affordances.v1`
- habits: `terrarium.habits.v1`
- situational events: `terrarium.situational-events.v1`
- spatial schema: `terrarium.spatial.v1`

Iteration 8D is a behavior/state + authored-art checkpoint. Object identity is now canonical: rolling, soft-nesting, delicate, and keepsake objects expose materially different affordances; interactions can persistently change later possibilities; and the renderer selects matching authored state variants. The semantic frame hash intentionally changes from 8C because object archetype, interaction state, transition count, and available affordances are now authoritative frame data.

Read `STATUS.md`, `ART_DIRECTION.md`, `VISUAL_STYLE_OVERHAUL.md`, `ROADMAP.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing. For renderer work, also inspect `display/art/manifest.json`, `display/art/palettes/materials.json`, `display/art/objects/`, `display/art/moss/`, and `display/web/app.js`.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, habits, event occurrence/lifecycle, attention outcomes, temporary affordances, semantic targets, physical route/approach/contact authority, **object identity, interaction state and available affordances**, history, time, and pacing;
- renderer may interpolate authoritative routes/object/event presentation and animate authored poses/state variants but may not invent navigation, event occurrence, intent, targets, object state, preferences, or history;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior rules: `terrarium-rules-v7-object-identity`; RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry remains `terrarium.spatial.v1`.

## Accepted object law after Iteration 8D

The six existing persistent objects map to four small archetypes:

- `blue_stone`, `acorn` → **rolling**;
- `red_thread` → **soft_nesting**;
- `amber_leaf` → **delicate**;
- `shell`, `glass_star` → **keepsake**.

Rolling objects use `settled → rolled → retrieve/settled`; a rolled object cannot simply be rolled again. Red thread uses `loose → rumpled → nested`; tugging is only available in `open_space`/`sleeping_nook`, rumpled state unlocks nest, and nested state removes repeat tug. Delicate/keepsake objects do not inherit generic play/nudge. Keepsakes may become `displayed` on the collection shelf. Carry/place can normalize state according to archetype and destination.

Object-specific arrangement preferences are tendencies layered beneath learned habits, not hard destinations. Existing habit anti-lock-in, recent-zone/object inhibition, possession continuity, supported sleep, situational-event behavior, exact replay, and additive migration remain authoritative.

## Accepted visual grammar after Iteration 8D

The accepted 8B room and 8C authored Moss vocabulary remain intact. `display/art/objects/` adds 13 authored state variants so object history is visible rather than only stored. The 16×16 / 25×15 art grid remains a composition grammar only; canonical movement, object positions, state transitions, event sources, and interaction anchors remain continuous semantic coordinates.

The scene grammar remains:

1. `BACK` — room shell and exterior/window view;
2. `STRUCTURE` — major furniture/architectural masses;
3. `SURFACE` — floor detail, rug, path wear/history, and floor-located events;
4. `WORLD` — bowls, persistent movable objects, and located environmental-event presentation;
5. `ACTORS` — Moss and carried-object acting;
6. `FRONT` — authored furniture lips/overhangs and supported sleep foreground causality;
7. `ALWAYS_FRONT` — reserved for rare justified foreground atmosphere.

Persistent history remains authoritative. Path wear, bedding compression, activity clutter, window marks, object arrangements, **object interaction state**, and situational events must derive from canonical state rather than decorative renderer memory.

## Behavioral law retained from Iterations 4–7

Short-horizon routine coherence, long-horizon `terrarium.habits.v1`, Iteration-6 repertoire, and Iteration-7 situational events remain active. A world event is canonical state with a bounded lifecycle and source location; it is an opportunity/interrupt, not automatically a behavior command. High-commitment object/sleep activity remains protected.

Event causality remains **event → perception/attention → reaction/defer → engagement/decision → aftermath**. Object causality now adds **identity/state → currently available affordance → contact/action → persistent state transition → later possibility**.

Keep using the compact architecture of **attention + affordances + persistent state + habits + bounded causal commitments**. A generic planner, needs/personality-stat model, quest system, dialogue system, inventory UI, or LLM action selector is not implied.

## Planned next iterations

`ROADMAP.md` and `VISUAL_STYLE_OVERHAUL.md` are authoritative unless direct canonical-runtime UAT exposes a more severe concrete defect:

1. **Iteration 8E — Atmospheric World** — persistent non-commanding ambient animation, richer window life, local warm lighting, and stronger whole-scene weather mood.
2. **Iteration 8F — Seasonal Terrarium** — add a slow canonical seasonal timescale and coordinated long-horizon visual transformation.
3. **Iteration 9 — Emergent Situations and Consequence Memory** — compose events, object state, arrangements, habits, and prior consequences into later opportunities.

The visual target remains a hand-authored late-16-bit life-RPG diorama: strict low-resolution grammar, readable silhouettes, richer saturated natural color, clustered shading, pragmatic perspective, layered depth, selective low-frame acting, non-commanding environmental motion, warm/cool lighting, slow world transformation, and persistent visible history. Do not copy external assets, exact palettes, characters, architecture, UI, or map structure.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, Python-3.10 grammar parsing, authored-art validation, technical/behavior/spatial/coherence/habit/repertoire/situational/**object-affordance** evaluators, exact replay, deterministic art-direction/temporal capture, and real 800×480 browser inspection. For major behavior changes, retain robustness coverage across seeds **1701 / 1702 / 42 / 999** and compare causal/semantic families rather than enum count alone.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific product work stays in Terrarium unless implementation evidence demonstrates a reusable substrate deficiency.
