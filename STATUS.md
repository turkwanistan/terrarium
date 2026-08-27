# Terrarium Status

Checkpoint: **POST-GEN17 PRODUCT CHECKPOINT — TEMPORAL RENDERING INTELLIGENCE**.

This is normal Terrarium development after the accepted Generation 17 pilot. It is **not Generation 18**.

## Current product state

Terrarium can now objectively prove rendered temporal correctness in addition to deterministic world state, exact replay, behavior, and static visual evidence. The production Canvas renderer still runs on ordinary `requestAnimationFrame`; development temporal mode can drive the same 800×480 drawing path at exact supplied timestamps and record machine-readable motion plus raster evidence.

Meaningful snapshot: `20260827T125248568567Z-temporal-rendering-intelligence` (seed 1701, tick 240). Evidence: `artifacts/temporal-rendering-intelligence.json` and `history/2026-08-27-temporal-rendering-intelligence.md`.

Inherited Gen17 guarantees remain intact: host-owned canonical creature/world state; deterministic simulation; append-only/hash-chained history; immutable snapshots + exact replay; disposable renderer; fixed hardware-neutral 800×480 `TerrariumFrame`; persistent objects/habitat wear/aftermath; canonical living state outside Git.

## Temporal rendering capability

The renderer now exposes reusable render-state calculation separately from RAF scheduling. Development-only fixture mode can render a real semantic source→target transition at exact timestamps and records:

- requested/render timestamp and source/target semantic tick;
- semantic/source/rendered Moss position and interpolation progress/ease;
- facing, pose/activity, carrying state, and carried-object rendered attachment;
- expected ambient-motion classes;
- actual 800×480 Canvas pixel identity plus regional luminance grids.

Repeated deterministic `left_walk` capture is byte-identical: SHA256 `f204f15e6ba50e1126642aca3761795a64954f799d7141c5ff0a1b126d15b410` on both runs.

Separate real RAF evidence: 110 frames / 1816.6 ms; p50 16.7 ms; p95 16.7 ms; max 16.8 ms; zero gaps >34 ms or >50 ms.

## Bounded renderer improvement

Measured temporal evidence justified one presentation-only change: Moss translation now uses quintic smootherstep rather than cubic smoothstep. Full deterministic left-walk endpoint sampled speed fell from 13.2308% of peak to 2.3047% of peak, giving gentler departure/arrival settling. The simulation clock, semantic frame, behavior RNG, world authority, and replay did not change. Legacy easing is development-comparison only.

## Objective reusable auditor

Promoted `temporal-render-auditor-r1`:

- content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`
- Forge evaluation: **6/6 PASS**
- genuine Terrarium pre-promotion tasks: **6/6 PASS**, reuse count 5
- dependencies: **none beyond Python standard library**

Independent outcome fixtures: **10/10 correct**, covering smooth motion, teleport, frozen motion, whole-scene jitter, facing mismatch, RAF stall, ambient rain/idle motion, attached/detached carried objects, and legacy endpoint settling.

Gen14 Evaluator Mutation Nursery: **10/10 dangerous mutants KILLED**, kill rate **1.0**, dangerous survivors **0**, invalid runs **0**, accepted state unchanged. Detection-power semantic digest `e3742464b3e7a3bd6bd488dd78f4f5c2bc4816ec41ff1e597b8787750f152217`.

Genuine renderer reuse: current left walk PASS; right walk PASS; carried walk PASS; idle control PASS; rain control PASS; real RAF PASS. Legacy left walk correctly FAILS `endpoint_settling`.

## Regression

- pytest: **17/17 PASS**
- JavaScript syntax: **PASS**
- Python 3.10 AST syntax compatibility: **PASS** across 22 project Python files
- technical evaluator: **PASS**
- exact replay: **PASS**
- behavior evaluator seed 1701 / 500: **PASS**
- action entropy: **3.151553 bits**, unchanged
- action distribution/object interaction metrics: unchanged

## Snapshot identity

- snapshot `20260827T125248568567Z-temporal-rendering-intelligence`
- deterministic seed **1701**, tick **240**
- frame SHA256 `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`
- renderer SHA256 `6d27df494be51bb7d8baa7c8683cbbd39893c1355eaf3785e194a860097e8578`

The semantic frame hash is intentionally unchanged from Temporal aftermath polish because this checkpoint changes testability and renderer interpolation, not canonical world outcome.

## SBC conclusion

No reusable SBC substrate deficiency was found. Existing mediated browser capture, bounded project evidence transport, Gen16 capability packs, Capability Forge, isolated Lab execution, Gen13 nested isolation, and Gen14 mutation testing were sufficient. Permanent Optiplex_Lab MCP surface remains 10 tools. Frozen Optiplex_MCP was not modified. **No Gen18 proposal is warranted.**

The existing promoted `simulation-behavior-auditor-r1` remains authoritative for simulation behavior. Candidate procedural memories remain non-authoritative unless their existing activation gates are met.

## Highest-value next product improvement

Use the new temporal proof system to make **present activity and accumulated aftermath feel causally connected**: subtle sleeping-nook, window, and activity-corner reactions while Moss is actually using those spaces, with explicit temporal checks preventing jitter/teleports/incorrect attachment. Do not claim those objective checks measure warmth or charm.

## Canonical runtime / remote

The canonical user-owned Moss runtime remains outside the available mediated development boundary and was not touched. The isolated development renderer was verified, but no canonical LAN URL is claimed.

`origin` remains `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Mediated push must use project-scoped credentials and must not bypass the credential boundary.
