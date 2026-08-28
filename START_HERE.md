# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 8B: Room Recomposition**

- history: `history/2026-08-27-pixel-art-overhaul-iteration8b.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8b.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8b-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8b-browser-uat.json`
- art-direction matrix: `artifacts/iteration8b-art-direction-matrix.json`
- snapshot: `snapshots/dev/20260828T023312695923Z-pixel-art-overhaul-iteration8b`
- seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `e0ad1ddeeb85b0bf23aba987e88394d10f58a641e3da2e398730238f8bf52d10`
- authored-art tree SHA256: `daaf4362afe7261e0bece29c7561aeb03333620bef5030898deeaec5d6f8ca96`
- authored asset count: **15**
- behavior rules remain: `terrarium-rules-v6-situational-attention`
- situational events remain: `terrarium.situational-events.v1`
- spatial schema remains: `terrarium.spatial.v1`

Iteration 8B is a renderer/art-composition checkpoint. Its seed-1701/tick-10080 semantic frame hash is identical to accepted Iterations 7 and 8A, proving authoritative simulation state remained unchanged.

Read `STATUS.md`, `ART_DIRECTION.md`, `VISUAL_STYLE_OVERHAUL.md`, `ROADMAP.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing. For renderer work, also inspect `display/art/manifest.json`, `display/art/palettes/materials.json`, representative authored assets, and `display/web/app.js`.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, habits, event occurrence/lifecycle, attention outcomes, temporary affordances, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes/object/event presentation and animate authored poses but may not invent navigation, event occurrence, intent, targets, preferences, or history;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior rules: `terrarium-rules-v6-situational-attention`; RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry remains `terrarium.spatial.v1`.

## Accepted visual grammar after Iteration 8B

The room now uses `display/art/` as the source of truth for its major static visual masses. The 16×16 / 25×15 art grid remains a composition grammar only; canonical movement, object positions, event sources, and interaction anchors remain continuous semantic coordinates.

The accepted scene grammar is:

1. `BACK` — room shell and exterior/window view;
2. `STRUCTURE` — major furniture/architectural masses;
3. `SURFACE` — floor detail, rug, path wear/history, and floor-located events;
4. `WORLD` — bowls, persistent movable objects, and located environmental-event presentation;
5. `ACTORS` — Moss and carried-object acting;
6. `FRONT` — authored furniture lips/overhangs and supported sleep foreground causality;
7. `ALWAYS_FRONT` — reserved for rare justified foreground atmosphere.

The palette bank is now materially richer and more saturated while remaining earthy: chromatic darks, warm timber, stronger vegetation ramps, distinct cloth blues, cool exterior values, and selective amber/terracotta/brass accents. Do not regress to uniform muted beige/brown treatment or expand into neon/glossy color.

Persistent history remains authoritative. Path wear, bedding compression, activity clutter, window marks, object arrangements, and situational events must continue to derive from canonical state rather than decorative renderer memory.

## Behavioral law after Iteration 7

Short-horizon routine coherence, long-horizon `terrarium.habits.v1`, Iteration-6 affordances, and Iteration-7 situational events remain authoritative and unchanged by 8A/8B.

A world event is canonical state with a bounded lifecycle and source location. It may be unseen or ignored; it is not automatically a behavior command. Moss may ignore, orient, defer, rarely interrupt a low-commitment activity, approach, engage, and recover depending on current commitment, salience, recent repetition, and deterministic attention choice. High-commitment object/sleep activity is protected.

Event causality remains **event → perception/attention → reaction/defer → engagement/decision → aftermath**. Temporary affordances such as moving sunlight remain canonical state; the renderer may depict them but cannot decide where or whether they exist.

Object manipulation, habits, possession continuity, spatial authority, supported sleep, recent-zone/object inhibition, exploration floors, and calm commitments continue to constrain situational response.

## Planned next iterations

`ROADMAP.md` and `VISUAL_STYLE_OVERHAUL.md` are authoritative unless direct canonical-runtime UAT exposes a more severe concrete defect:

1. **Iteration 8C — Moss Sprite Overhaul** — replace remaining procedural hero poses with true authored low-frame sprites while preserving current semantic actions/timing/contact authority.
2. **Iteration 8D — Object Identity and Stateful Affordances** — resume behavior expansion with object-specific state transitions and matching authored visual variants.
3. **Iteration 8E — Atmospheric World** — persistent non-commanding ambient animation, richer window life, local warm lighting, and stronger weather mood.
4. **Iteration 8F — Seasonal Terrarium** — add a slow canonical seasonal timescale and coordinated long-horizon visual transformation.
5. **Iteration 9 — Emergent Situations and Consequence Memory** — compose events, object state, arrangements, habits, and prior consequences into later opportunities.

The visual target is a hand-authored late-16-bit life-RPG diorama: strict low-resolution grammar, readable silhouettes, richer saturated natural color, clustered shading, pragmatic perspective, layered depth, selective low-frame acting, non-commanding environmental motion, warm/cool lighting, slow world transformation, and persistent visible history. This is a system-level target; do not copy external assets, exact palettes, characters, architecture, UI, or map structure.

A generic planner, needs/personality-stat model, quest system, dialogue system, or LLM action selector is not implied. Keep pushing the existing model of **attention + affordances + persistent state + habits + bounded causal commitments**.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, Python-3.10 grammar parsing, authored-art schema/grid validation, technical/behavior/spatial/coherence/habit/repertoire/situational evaluators, exact replay, deterministic art-direction/temporal capture, and real 800×480 browser inspection. For major behavior changes, retain robustness coverage across seeds **1701 / 1702 / 42 / 999** and compare causal/semantic families rather than enum count alone.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific product work stays in Terrarium unless implementation evidence demonstrates a reusable substrate deficiency.
