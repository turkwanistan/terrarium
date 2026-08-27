# Temporal rendering intelligence — 2026-08-27

This is a normal post-Gen17 Terrarium product checkpoint, not Generation 18.

## Goal

Add objective evidence for rendered behavior over time without moving authority into the renderer, changing the simulation clock, or adding production CV/video dependencies.

## Renderer architecture

The Canvas renderer now separates reusable render state from RAF orchestration. Production continues to use normal `requestAnimationFrame` timestamps. Development-only temporal mode loads a bounded source/target `TerrariumFrame` transition, sets `fetchedAt=0`, and renders exact supplied timestamps through the same 800×480 drawing implementation.

Per-sample telemetry includes requested timestamp; source/target tick; semantic/source/rendered Moss position; interpolation progress/ease; facing; pose/activity; carrying state and rendered attachment; ambient-motion classes; actual Canvas pixel identity; and a regional luminance grid. Development endpoints are disabled unless explicit CLI fixture/output flags are supplied.

The same `left_walk` transition captured twice produced identical evidence SHA256 `f204f15e6ba50e1126642aca3761795a64954f799d7141c5ff0a1b126d15b410`.

A separate real-RAF probe measured 110 frames over 1816.6 ms: p50/p95 16.7 ms, max 16.8 ms, zero gaps over 34 ms and zero over 50 ms.

## Real renderer improvement

Temporal measurement justified one bounded presentation change: creature translation interpolation moved from cubic smoothstep to quintic smootherstep. On the full deterministic left-walk sequence, endpoint sampled speed fell from 13.2308% of peak to 2.3047% of peak, producing gentler departure/arrival settling. Simulation state, frame contract, behavior RNG, and replay are unchanged. The legacy easing exists only as a development comparison path.

## Objective reusable capability

The refreshed capability requirement classified `temporal-render-auditor` as `MISSING_VALUABLE`; the existing Forge substrate was sufficient to build it without permanent MCP growth.

Promoted capability:

- name: `temporal-render-auditor-r1`
- content hash: `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- evaluator hash: `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`
- Forge evaluation: 6/6 PASS
- genuine Terrarium tasks before promotion: 6/6 PASS
- dependencies: Python standard library only

An earlier candidate seal accidentally contained generated `__pycache__`; it was explicitly expired before evaluation/promotion and is non-authoritative.

## Independent fixtures

Expected outcomes were independently specified and all 10 discriminated correctly:

- smooth translation — PASS
- teleport midway — FAIL
- frozen Moss during semantic movement — FAIL
- random whole-scene jitter — FAIL
- wrong-facing movement — FAIL
- long animation-frame stall — FAIL
- normal rain/idle animation — PASS
- smoothly attached carried object — PASS
- detached/jumping carried object — FAIL
- legacy endpoint settling — FAIL

## Evaluator mutation testing

Gen14 Evaluator Mutation Nursery ran 10 dangerous mutants under the accepted Gen13 isolation path. All 10 were killed; dangerous mutation kill rate 1.0; dangerous survivors 0; invalid runs 0; accepted state unchanged. Detection-power semantic digest: `e3742464b3e7a3bd6bd488dd78f4f5c2bc4816ec41ff1e597b8787750f152217`.

Mutants challenged teleport, frozen-motion, facing, whole-scene jitter, carried attachment, endpoint settling, stall thresholds, fail-open scene-change handling, and trust in declared PASS state.

## Genuine Terrarium reuse

Promoted-candidate real-task evidence before promotion:

- left walk — PASS
- right walk — PASS
- carried walk — PASS
- idle control — PASS
- rain control — PASS
- real RAF pacing — PASS
- legacy left-walk comparison — expected FAIL on `endpoint_settling`

## Regression

- pytest: 17/17 PASS
- JavaScript syntax: PASS
- Python 3.10 AST syntax compatibility: PASS across 22 project Python files
- technical evaluator: PASS
- exact snapshot + subsequent-event replay: PASS
- behavior evaluator seed 1701 / 500: PASS
- action entropy: 3.151553 bits, unchanged
- action distribution/object interaction metrics: unchanged from inherited checkpoint

## Snapshot

Exactly one meaningful development snapshot was created:

- `20260827T125248568567Z-temporal-rendering-intelligence`
- seed 1701 / tick 240
- frame SHA256 `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`
- renderer SHA256 `6d27df494be51bb7d8baa7c8683cbbd39893c1355eaf3785e194a860097e8578`

The frame hash intentionally remains identical to the prior checkpoint; the bounded improvement is renderer-only.

Primary retained evidence: `artifacts/temporal-rendering-intelligence.json`, compact inputs under `artifacts/temporal-audit-inputs/`, `artifacts/temporal-render-fixtures.json`, `artifacts/temporal-lab-transport.json`, and `artifacts/temporal-capability-gap.json`. Larger raw browser sequences were discarded after compact evidence was retained.

## SBC conclusion

No reusable Self-Building Computer substrate deficiency was found. Existing browser mediation, Gen16 project transport/capability packs, Capability Forge, isolated Lab execution, Gen13 nested isolation, and Gen14 mutation testing were sufficient. Permanent Lab MCP surface remains 10 tools. Frozen Optiplex_MCP was not modified. This does not warrant Gen18.

The canonical user-owned Moss runtime was not touched from the mediated development boundary, so no LAN deployment URL is claimed.
