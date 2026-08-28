# START HERE

Terrarium is a normal product built after the accepted Self-Building Computer Generation 17 pilot. Repository/live state and evaluation evidence override chat memory.

## Current checkpoint

**Pixel-Art Overhaul — Iteration 6: Behavioral Repertoire and World Affordances**

- history: `history/2026-08-27-pixel-art-overhaul-iteration6.md`
- evidence: `artifacts/pixel-art-overhaul-iteration6.json`
- evaluation: `artifacts/pixel-art-overhaul-iteration6-evaluation.json`
- snapshot: `snapshots/dev/20260827T233841118223Z-pixel-art-overhaul-iteration6`
- seed/tick: **1701 / 10080**
- semantic frame SHA256: `0a759f58fa022f3dcbf7dd4de33c632bb9ee9366b82e0b077d71eacd6314102e`
- renderer JS SHA256: `66a80f9e86d3242a2c99903956faa39873dd7dbfc0233869af8c2952bb56cd19`
- behavior rules: `terrarium-rules-v5-behavioral-repertoire`
- behavior context: `terrarium.behavior-context.v1`
- habit profile: `terrarium.habits.v1`
- affordance history: `terrarium.affordances.v1`
- spatial schema: `terrarium.spatial.v1`

Read `STATUS.md`, `ART_DIRECTION.md`, `ROADMAP.md`, `plan.md`, `terrarium.md`, and the latest history entry before editing.

## Authority contracts

- semantic/reference frame: **800×480**;
- pixel-native art surface: **400×240**, exact 2× nearest-neighbor, smoothing off;
- world engine owns behavior, habits, affordance consequences, semantic targets, physical route/approach/contact authority, object state, history, time, and pacing;
- renderer may interpolate authoritative routes/object displacement and animate authored poses but may not invent navigation, intent, targets, preferences, or history;
- heartbeat: **3 real seconds**; world advance: **1 minute/heartbeat**; full day ~**72 real minutes**;
- behavior rules: `terrarium-rules-v5-behavioral-repertoire`; RNG stream remains pinned to `terrarium-rules-v3-routine-coherence`; geometry: `terrarium.spatial.v1`.

## Behavioral law after Iteration 6

Short-horizon routine coherence and long-horizon `terrarium.habits.v1` remain authoritative. Iteration 6 adds affordances rather than a planner: Moss can investigate and nudge objects, carry them into habit-shaped arrangements, loaf/groom/stretch in plausible places, and react to real deterministic weather opportunities. Activities still have bounded beginnings, middles, endings, commitments, and settling periods.

`terrarium.affordances.v1` is aftermath/history, not a drive model. It records only completed post-migration activity and may support later causal presentation/evaluation. It does not schedule Moss or reconstruct nonexistent pre-upgrade behavior. Habits may bias where comfort and arrangement activities occur, but recent-zone/object inhibition, exploration floors, spatial authority, possession continuity, weather, and activity commitments prevent lock-in.

Object manipulation must remain consequential. A nudge changes authoritative object coordinates, exposes the new position to future behavior, and normally earns a same-object re-inspection. A carried object has one chosen arrangement destination and is physically placed into an authored slot. Environmental reaction is similarly causal: noticing rain/mist may redirect Moss to the window, but the reaction is not just an animation label.

## Planned next iterations

`ROADMAP.md` is the authoritative forward product sequence unless direct canonical-runtime UAT exposes a more severe defect:

1. **Iteration 7 — Situational Events and Environmental Attention** — make the world present canonical opportunities and interruptions; target **event → perception → reaction → decision/engagement → aftermath**, including ignore/defer outcomes.
2. **Iteration 8 — Object Identity and Stateful Affordances** — make different object classes enable different interactions and persistent state transitions.
3. **Iteration 9 — Emergent Situations and Consequence Memory** — let events, object state, arrangements, and habits create later opportunities and multi-stage situations across longer horizons.

These remain normal Terrarium product iterations. A general planner, needs/personality-stat model, quest system, or LLM action selector is not implied by this roadmap.

## Regression procedure

Run `python -m pytest -q`, `node --check display/web/app.js`, Python-3.10 grammar parsing, technical/behavior/spatial/coherence/habit/repertoire evaluators, exact replay, deterministic temporal capture, and real 800×480 browser inspection. For major behavior changes, run coherence and habit robustness across seeds **1701 / 1702 / 42 / 999** and compare semantic activity families rather than enum count alone.

Promoted reusable capabilities remain:
- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`

Do not invent Gen18 by cadence. Terrarium-specific product work stays in Terrarium unless implementation evidence demonstrates a reusable substrate deficiency.
