# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 7: Situational Events and Environmental Attention**

- history: `history/2026-08-27-pixel-art-overhaul-iteration7.md`
- evidence: `artifacts/pixel-art-overhaul-iteration7.json`
- situational evaluation: `artifacts/pixel-art-overhaul-iteration7-situations.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration7-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration7-browser-uat.json`
- snapshot: `snapshots/dev/20260828T010131008922Z-pixel-art-overhaul-iteration7`
- seed/tick: **1701 / 10080**
- semantic frame SHA256: `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`
- renderer JS SHA256: `c9b3e44af04bfba888d335add0bce822ffc59968029cbd13b8cbbee22c5e0fe2`
- behavior rules: `terrarium-rules-v6-situational-attention`
- situational events: `terrarium.situational-events.v1`
- behavior context: `terrarium.behavior-context.v1`
- habit profile: `terrarium.habits.v1`
- affordance history: `terrarium.affordances.v1`
- spatial schema: `terrarium.spatial.v1`

Read `STATUS.md`, `ART_DIRECTION.md`, `ROADMAP.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, habits, event occurrence/lifecycle, attention outcomes, temporary affordances, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes/object/event presentation and animate authored poses but may not invent navigation, event occurrence, intent, targets, preferences, or history;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior rules: `terrarium-rules-v6-situational-attention`; RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry remains `terrarium.spatial.v1`.

## Behavioral law after Iteration 7

Short-horizon routine coherence, long-horizon `terrarium.habits.v1`, and Iteration-6 affordances remain authoritative. Iteration 7 adds a compact deterministic situational layer rather than a planner. The initial catalog is `sunlight`, `bird`, `rain_intensify`, `thunder`, `moth`, and `leaf_tap`.

A world event is canonical state with a bounded lifecycle and source location. It may be unseen or ignored; it is not automatically a behavior command. Moss may ignore, orient, defer, rarely interrupt a low-commitment activity, approach, engage, and then recover depending on current commitment, salience, recent repetition, and deterministic attention choice. High-commitment object/sleep activity is protected. Events must remain opportunities, not compulsory interrupt handlers.

Event causality is explicit: **event → perception/attention → reaction/defer → engagement/decision → aftermath**. The same low-level action can therefore carry different meaning from its cause. Window watching may be casual, bird-driven, rain-driven, or part of another bounded situation without multiplying action enums merely for labels.

Temporary affordances must be authoritative. The moving sunlight patch is the first example: its current walkable location exists in canonical state, Moss can loaf at that location while it exists, may follow one shift, and loses that opportunity when the patch moves or expires. The renderer may depict the patch but cannot decide where or whether it exists.

Object manipulation, habits, possession continuity, spatial authority, supported sleep, recent-zone/object inhibition, exploration floors, and calm commitments continue to constrain situational response. Iteration 7 is additive: ordinary autonomous life still accounts for more than 91% of decisions in the accepted seven-day matrix.

## Planned next iterations

`ROADMAP.md` is authoritative unless direct canonical-runtime UAT exposes a more severe concrete defect:

1. **Iteration 8 — Object Identity and Stateful Affordances** — make object class materially alter the interactions and persistent state transitions available.
2. **Iteration 9 — Emergent Situations and Consequence Memory** — let event state, object state, arrangements, and habits compose into later opportunities and multi-stage situations.

A generic planner, needs/personality-stat model, quest system, dialogue system, or LLM action selector is not implied. First keep pushing the existing model of **attention + affordances + persistent state + habits + bounded causal commitments**.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, Python-3.10 grammar parsing, technical/behavior/spatial/coherence/habit/repertoire/situational evaluators, exact replay, deterministic temporal capture, and real 800×480 browser inspection. For major behavior changes, retain robustness coverage across seeds **1701 / 1702 / 42 / 999** and compare causal/semantic families rather than enum count alone.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific product work stays in Terrarium unless implementation evidence demonstrates a reusable substrate deficiency.
