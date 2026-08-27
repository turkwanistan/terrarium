# Post-Gen17 product checkpoint — Lived-in staging

Date: 2026-08-27

This is normal Terrarium development after the accepted Gen17 pilot. It is **not Generation 18**.

## Product change

The checkpoint strengthens the core thesis, “Something has been happening here while I was gone,” without adding dashboards, preferences, conversation, hardware code, or new autonomous mechanics.

Two bounded changes were made:

1. **Habitat-aware object staging.** Autonomous `place` actions now choose deterministic authored positions for each habitat zone rather than random offsets. Existing placed objects reserve nearby slots, so collections remain legible instead of overlapping.
2. **Persistent travel routes.** The renderer now turns accumulated `path_wear` into actual worn routes through the diorama, with subtle settled/scuffed patches beneath frequently moved possessions. These are renderer cues derived from canonical history; the renderer remains disposable and non-authoritative.

`TerrariumFrame` now exposes the already-canonical `times_inspected` object field so future presentation work can use inspection history without moving authority into the display.

## Visual/storytelling evidence

A deterministic comparison is stored in `artifacts/visual-storytelling-comparison.json`:

- fresh seed 1701 / tick 0: 0 moved objects, 0 visible routes, 0 authored-anchor objects;
- accepted Gen17 baseline / tick 240: 3 moved objects, 5 visible routes, 0 authored-anchor objects, 9 persistent marks;
- improved accelerated life / tick 720: 6 moved objects, 5 strongly worn routes, 6/6 placed objects at authored anchors, 6 settled-use cues, 10 persistent marks.

The comparison is deliberately objective and does not claim to be a subjective visual-quality oracle.

A same-seed/same-horizon counterfactual against untouched Gen17 commit `0fa3952` is stored in `artifacts/visual-storytelling-counterfactual.json`. At tick 720 both old and new worlds have shelf_count 5 and total path wear 226, but old Gen17 has only 4 unique coordinates for 6 placed objects: two pairs of shelf objects overlap exactly. The new implementation has 6 unique authored coordinates for 6 placed objects. This isolates a genuine layout/storytelling improvement from simply simulating for longer.

## Browser inspection

The real Canvas renderer was inspected at 800×480 through the mediated browser:

- a fresh isolated world was verified at tick 0;
- the accepted Gen17 deterministic snapshot was captured before implementation for before-state comparison;
- an improved isolated world was verified at tick 720, with 5 objects visibly represented by the shelf collection state and all 10 persistent wear marks present;
- the new deterministic development snapshot was opened through the actual renderer and verified at tick 240.

Meaningful development snapshot:

- `snapshots/dev/20260827T050435058386Z-lived-in-staging`
- frame SHA256 `1070774ead7f46638b3a409d1a7896ffdcf7f49c8fb582e6bf8171aec3ca2d53`

## Regression evidence

Before history/documentation updates:

- pytest: 13/13 PASS;
- technical evaluator: PASS, exact replay, event-chain integrity, append-only enforcement, restart equality, fixed 800×480 frame;
- behavior evaluator seed 1701 / 500 steps: PASS with all 10 action classes, entropy 3.151553 bits, 28 placements, 28 pickups, 58 inspections, all 6 objects moved, 10 persistent marks;
- behavior distribution is unchanged from the accepted Gen17 reference run.

Final regression is rerun after documentation changes before commit.

## Self-Building Computer reuse

No new reusable capability gap was required.

The existing promoted `simulation-behavior-auditor-r1` capability was verified at content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f` with evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae` and reused on a held-out 180-event post-change stream. It passed with 10 action classes, entropy 3.174454 bits, 42 object interactions, and `sequence_ok=true`.

The successful real reuse was recorded as procedural episode `ep_091c8bfcdd8027f0ba2c`. Re-distillation did **not** activate the memory: the held-out applicability check correctly failed because the recorded episode environment omitted the required `input_schema_hash` precondition. New memory object `3eaa33c60f47c1d4c2255ae518fdb573f111f10e8f389f045dcf050c39a1eed8` remains `CANDIDATE`. The gate was left intact; no authority/precondition weakening was attempted.

Operational Optiplex_Lab remained `gen6-experience-memory-r1-dc0d2cb41595`, permanent tool surface 10. Frozen Optiplex_MCP was not modified.

## Highest-value next product work

Keep the same direction but make **specific activities leave distinct physical aftermath** rather than adding more mechanics: e.g. sleeping gradually rumples the nook, repeated window-watching leaves subtle window/sill traces, and repeated activity-corner use accumulates small paper/work marks. The normal diorama should communicate *what Moss has been doing*, not only that traffic occurred.
