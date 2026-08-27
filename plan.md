# Terrarium Plan

## Completed Gen17 initial scope

### Phase 0 — contracts and skeleton
- deterministic canonical world/state model
- versioned append-only meaningful events with hash chain
- deterministic seed/rule/tick entropy
- SQLite canonical state + immutable snapshots + inspectable JSONL event history
- exact snapshot + subsequent-event replay
- fixed hardware-neutral `terrarium.frame.v1` at exactly 800×480
- persistent world HTTP service; renderer is read-only/disposable

### Phase 1 — something visibly alive
- one autonomous creature (`Moss`)
- idle/walk/explore/rest/sleep/wake/look-outside behavior
- day/night/environment cycle
- multiple named habitat zones
- Canvas interpolation/animation and expressive creature state
- world continues while browser is closed

### Phase 2 — persistent objects
- six persistent objects
- inspect/carry/place interactions
- collection shelf and persistent zones
- visible habitat wear/accumulation
- restart persistence and exact replay of arrangements

## Completed normal product checkpoint — Lived-in staging

The first post-Gen17 product iteration strengthened accumulated-life legibility without adding new mechanics:

- deterministic authored placement slots per habitat zone;
- collision-aware placement so persistent collections do not overlap;
- connected worn routes derived from canonical `path_wear`;
- settled/scuffed cues beneath repeatedly moved possessions;
- `times_inspected` exposed through the semantic frame for later visual storytelling.

Evidence: `history/2026-08-27-lived-in-staging.md`, `artifacts/visual-storytelling-comparison.json`, `artifacts/visual-storytelling-counterfactual.json`, and snapshot `20260827T050435058386Z-lived-in-staging`.

## Completed normal product checkpoint — Activity aftermath

- persistent history-derived counters for sleeping-nook sleep, window-watching, and activity-corner use;
- rumpled/compressed sleeping nook from actual sleep history;
- pane/sill traces from repeated window watching;
- progressively rearranged papers/work marks from activity-corner use;
- same-horizon counterfactual proves legacy frame outcome is unchanged except the new aftermath payload.

Evidence: `history/2026-08-27-activity-aftermath.md`, `artifacts/activity-aftermath-comparison.json`, snapshot `20260827T054359565518Z-activity-aftermath`.

## Completed normal product checkpoint — Temporal aftermath polish

- activity-aftermath counter changes interpolate over 1.8 seconds in the renderer;
- 26 authored aftermath layers fade in progressively instead of appearing through integer count buckets;
- stable hash-derived micro-variation keeps papers/traces organic without `Math.random`;
- persistent window traces respond subtly to rain/mist/clear conditions;
- bedding compression, pillow drift, and creases grow continuously from actual sleep history;
- generic path wear is quieter so activity-specific history retains visual priority;
- the canonical seed-1701/tick-240 frame is unchanged from the previous checkpoint.

Evidence: `history/2026-08-27-temporal-aftermath-polish.md`, `artifacts/temporal-aftermath-polish.json`, snapshot `20260827T115103702156Z-temporal-aftermath-polish`.

## Completed normal product checkpoint — Temporal rendering intelligence

- production renderer continues to use ordinary `requestAnimationFrame`; development mode can render the same Canvas implementation at exact supplied timestamps;
- deterministic source→target frame fixtures cover left/right movement, carried movement, idle control, and rain control;
- machine-readable temporal telemetry records semantic/rendered trajectory, interpolation, facing, pose/activity, carried-object attachment, ambient classes, and compact raster evidence from the actual 800×480 Canvas;
- real RAF pacing is measured separately from manual-clock correctness;
- promoted reusable `temporal-render-auditor-r1` objectively detects teleports, frozen semantic movement, reversals, facing mismatch, whole-scene jitter, carried-object detachment, semantic→visual causality failure, endpoint settling, and RAF stalls;
- independent fixture outcomes were 10/10 correct; Gen14 mutation testing killed 10/10 dangerous mutants with zero survivors;
- genuine Terrarium left/right/carry/idle/rain/RAF tasks passed;
- measured endpoint behavior justified one renderer-only change from cubic smoothstep to quintic smootherstep, reducing sampled endpoint speed from 13.2308% to 2.3047% of peak on the canonical left-walk capture;
- no production CV/video dependency, permanent MCP growth, world-model change, or SBC Gen18 substrate work was required.

Evidence: `history/2026-08-27-temporal-rendering-intelligence.md`, `artifacts/temporal-rendering-intelligence.json`, compact evidence under `artifacts/temporal-audit-inputs/`, snapshot `20260827T125248568567Z-temporal-rendering-intelligence`.

## Evaluation loop

Keep the development loop: implement → deterministic accelerated run → technical/behavior evaluation → deterministic temporal capture where relevant → independent RAF probe where relevant → live browser inspection → identify weakness → bounded change → replay/regression.

Primary invariants/metrics: replay equality; event-chain integrity; restart equality; Python 3.10 syntax compatibility; action diversity/entropy; non-sleep repetition; object pickups/placements/inspections; moved-object count; persistent habitat marks; renderer authority/synchronization; deterministic temporal-capture equality; subject trajectory/facing/attachment/causality; independent real-RAF pacing; event storage growth; and direct visual comparison against the accepted deterministic snapshot timeline.

Use project-factory / Experiment Capsule / counterfactual / Forge capabilities only when a real engineering uncertainty or reusable capability gap justifies them. Do not create Self-Building Computer generations merely because Terrarium advances.

## Next product iteration

Highest-value target: make **present activity and accumulated aftermath feel causally connected**. While Moss sleeps, watches the window, or uses the activity corner, the already-existing traces should respond subtly to the current action/environment without moving authority into the renderer or adding new mechanics. Use the promoted temporal auditor to prove timing/attachment/stability correctness while keeping subjective warmth/charm as human visual judgment.

Objective temporal correctness is now covered. Automated subjective artistic-quality judging remains intentionally out of scope; do not reinterpret temporal metrics as a warmth/charm oracle.

## Later

Only after the software experience is compelling: preferences/routines, richer long-term identity, optional interaction/conversation, and hardware renderer experiments. Hardware must remain a renderer/client of the same host-owned creature and history.

## Checkpoint discipline

For each meaningful user-visible iteration: implement → test/evaluate → run/inspect → capture one deterministic development snapshot → update `STATUS.md` / history → commit → push attempt. Avoid snapshotting every small edit and never commit the live SQLite/event ledger. Git is product-development history, not a backup of Moss's living state.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 1

- replaced the smooth storybook/vector-like presentation with a true 400×240 pixel-native Canvas art surface;
- exact 2× nearest-neighbor presentation preserves the fixed 800×480 reference contract without changing canonical semantic coordinates;
- rebuilt Moss as a brown floppy-eared gameplay sprite with side/three-quarter orientation, no default glasses, and pixel key poses for the existing action vocabulary;
- rebuilt the core room with clustered stepped shading, selective outlines, moss/walnut/amber/dusty-blue/cream palette families, hard-edged depth, and persistent-history marks;
- moved day/dawn/dusk/night/rain/mist presentation to finite palette/value steps and sparse pixel effects;
- preserved canonical action commitments, targets, contact/attachment/place/sleep semantics, 72-minute day, ~9-minute weather blocks, and calm decision cadence;
- proved exact raster scaling across 16 deterministic real-browser scenarios / 176 sampled frames with zero scale errors;
- the original promoted temporal auditor exposed a valid integer-grid endpoint-settling coverage gap;
- existing Capability Forge produced promoted `grid-quantized-temporal-render-auditor-r1` (`57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`), preserving the original 10/10 oracle and killing 2/2 dangerous Gen14 mutants;
- no SBC substrate change or Gen18 work was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration1.md`, `artifacts/pixel-art-overhaul-iteration1.json`, snapshot `20260827T183924459328Z-pixel-art-overhaul-iteration1`.

## Next product iteration

Pixel-Art Overhaul, Iteration 2 should be driven by direct human UAT of the accepted first pass. Prefer craft over feature count: refine Moss silhouette/ears/legs/tail and key poses; improve room object silhouettes and material clusters; tune composition/negative space; strengthen furniture depth and foreground overlaps; refine environmental palettes and rain readability; and make each existing interaction legible at a glance. Preserve the exact 400×240 → 800×480 pipeline and the grid-aware temporal rejection gate.
