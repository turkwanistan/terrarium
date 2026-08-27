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

## Evaluation loop

Keep the development loop: implement → deterministic accelerated run → technical/behavior evaluation → live browser inspection → identify weakness → bounded change → replay/regression.

Primary invariants/metrics: replay equality; event-chain integrity; restart equality; Python 3.10 syntax compatibility; action diversity/entropy; non-sleep repetition; object pickups/placements/inspections; moved-object count; persistent habitat marks; renderer authority/synchronization; event storage growth; and direct visual comparison against the accepted deterministic snapshot timeline.

Use project-factory / Experiment Capsule / counterfactual / Forge capabilities only when a real engineering uncertainty or reusable capability gap justifies them. Do not create Self-Building Computer generations merely because Terrarium advances.

## Next product iteration

Highest-value target: make **present activity and accumulated aftermath feel causally connected**. While Moss sleeps, watches the window, or uses the activity corner, the already-existing traces should respond subtly to the current action/environment without moving authority into the renderer or adding new mechanics.

Automated subjective/temporal visual-quality judging remains a known weak area. Treat it honestly; do not call a static metric a warmth/smoothness oracle.

## Later

Only after the software experience is compelling: preferences/routines, richer long-term identity, optional interaction/conversation, and hardware renderer experiments. Hardware must remain a renderer/client of the same host-owned creature and history.

## Checkpoint discipline

For each meaningful user-visible iteration: implement → test/evaluate → run/inspect → capture one deterministic development snapshot → update `STATUS.md` / history → commit → push attempt. Avoid snapshotting every small edit and never commit the live SQLite/event ledger. Git is product-development history, not a backup of Moss's living state.
