# Terrarium Status

Checkpoint: **POST-GEN17 PRODUCT CHECKPOINT — LIVED-IN STAGING**.

This is normal Terrarium development after the accepted Generation 17 pilot. It is **not Generation 18**.

## Current product state

Inherited Gen17 guarantees remain intact:

- fixed hardware-neutral logical renderer: **800×480**;
- persistent canonical creature/world state outside the renderer;
- deterministic seeded simulation and exact snapshot + subsequent-event replay;
- append-only/hash-chained event history;
- process/browser restart persistence;
- autonomous idle/walk/explore/rest/sleep/wake/look-outside/inspect/carry/place behavior;
- multiple habitat zones, persistent objects, and persistent habitat wear;
- canonical living state is user-owned outside Git; renderer is disposable/non-authoritative.

Latest visible improvement:

- autonomous object placements now use deterministic authored habitat positions instead of random scatter;
- placement collision avoidance keeps small collections legible;
- accumulated `path_wear` now renders as connected worn travel routes through the diorama;
- frequently moved possessions leave subtle settled/scuffed physical cues;
- `TerrariumFrame` exposes the already-canonical `times_inspected` field for future presentation work without moving authority into the renderer.

Meaningful development snapshot:

- `20260827T050435058386Z-lived-in-staging`
- deterministic seed **1701**, tick **240**
- frame SHA256 `1070774ead7f46638b3a409d1a7896ffdcf7f49c8fb582e6bf8171aec3ca2d53`

## Evidence

Latest checkpoint regression before commit:

- pytest: **13/13 PASS**;
- technical evaluator: **PASS** — exact replay, event-chain integrity, append-only SQLite enforcement, restart equality, fixed 800×480 frame;
- behavior evaluator seed 1701 / 500 steps: **PASS** — 10 action classes, entropy **3.151553 bits**, 28 placements, 28 pickups, 58 inspections, all 6 objects moved, 10 persistent habitat marks;
- behavior distribution remained identical to the accepted Gen17 reference run.

Visual-storytelling comparison (`artifacts/visual-storytelling-comparison.json`):

- fresh tick 0: 0 moved objects, 0 visible routes, 0 authored-anchor objects, 0 marks;
- accepted Gen17 baseline tick 240: 3 moved objects, 5 visible routes, 0 authored-anchor objects, 9 marks;
- improved accelerated life tick 720: 6 moved objects, 5 strongly worn routes, 6/6 placed objects at authored anchors, 6 settled-use cues, 10 marks.

Same-seed/same-horizon counterfactual (`artifacts/visual-storytelling-counterfactual.json`):

- old Gen17 commit `0fa3952`, seed 1701 / tick 720: shelf_count 5, total path wear 226, 6 placed objects but only **4 unique coordinates** because two shelf-object pairs overlap;
- current implementation, same seed/tick: shelf_count 5, total path wear 226, **6 unique authored coordinates for 6 placed objects**.

This isolates a real product/layout improvement from merely simulating longer.

## Browser inspection

The actual Canvas renderer was inspected at 800×480 through the mediated browser:

- fresh isolated world verified at tick 0;
- Gen17 deterministic baseline captured before implementation;
- improved isolated world verified at tick 720 with shelf_count 5 and all 10 persistent marks;
- new deterministic snapshot opened through the renderer and verified at tick 240.

The visual comparison artifacts intentionally do **not** claim to be a subjective warmth/smoothness oracle. Automated temporal/subjective visual-quality judging remains weak.

## Self-Building Computer / capability evidence

No new reusable capability gap was needed for this checkpoint.

Existing promoted capability:

- `simulation-behavior-auditor-r1`
- content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae`

Held-out post-change reuse: **PASS** on 180 ordered events with 10 action classes, entropy 3.174454 bits, 42 object interactions, and `sequence_ok=true`.

The successful reuse was recorded as procedural episode `ep_091c8bfcdd8027f0ba2c`. Re-distillation produced candidate memory `3eaa33c60f47c1d4c2255ae518fdb573f111f10e8f389f045dcf050c39a1eed8`, but held-out activation failed closed because the recorded episode environment omitted the required `input_schema_hash` precondition. It remains **CANDIDATE**. No gate or authority rule was weakened.

Operational Lab remains `gen6-experience-memory-r1-dc0d2cb41595`; permanent MCP surface remains 10. Frozen Optiplex_MCP was not modified.

## Inherited Gen17 runtime proof

- browser close/reopen advanced authoritative tick/event **36 → 63** while the renderer was closed;
- process restart resumed persisted state and reached tick/event **87** rather than resetting;
- stopped final live proof reached **402 events/ticks** with exact replay hash `b3d10eda99f8b3ba580043d4d7c40bd1ce0cde0f9cbc45cde019fb3d1fc21a1b`;
- compact event redesign reduced the observed 100-event JSONL footprint from ~889 KB to ~124 KB while preserving replay.

## Highest-value next product improvement

Make existing activities leave **distinct physical aftermath**: rumpled/settled sleeping-nook state from repeated sleep, subtle window/sill traces from repeated watching, and accumulated work/paper traces from activity-corner use. The next checkpoint should make an observer infer *what Moss has been doing*, not simply that the room has traffic.

Hardware, learned preferences/routines, conversation, and broader mechanics remain later work unless this visual-storytelling direction exposes a concrete prerequisite.

## Development / runtime policy

- milestone snapshots: `snapshots/dev/`; standard comparison scene seed 1701 / step 240;
- local gallery: `/snapshots/`; renderer/source hashes pin historical identity;
- canonical trusted-LAN launch: `scripts/run_lan.sh`;
- runtime state defaults to `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` and must remain outside Git;
- repo-local `data/*` is ignored except `.gitkeep` and is development/legacy-only;
- normal development creates one tested commit/push attempt per meaningful checkpoint.

## Remote

- `origin`: `git@github.com:turkwanistan/terrarium.git`
- `main` tracks `origin/main`
- mediated push uses project-scoped credentials and must not be bypassed by copying secrets into the repo.
