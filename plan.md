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

## Evaluation loop

Keep the development loop: implement → deterministic accelerated run → technical/behavior evaluation → live browser inspection → identify weakness → bounded change → replay/regression.

Primary invariants/metrics: replay equality; event-chain integrity; restart equality; Python 3.10 syntax compatibility; action diversity/entropy; non-sleep repetition; object pickups/placements/inspections; moved-object count; persistent habitat marks; renderer authority/synchronization; event storage growth; and direct visual comparison against the accepted deterministic snapshot timeline.

Use project-factory / Experiment Capsule / counterfactual / Forge capabilities only when a real engineering uncertainty or reusable capability gap justifies them. Do not create Self-Building Computer generations merely because Terrarium advances.

## Next product iteration

Highest-value target: make **specific existing activities leave distinct physical aftermath** in the normal diorama.

Examples worth testing, without automatically implementing all of them:

- repeated sleep/rest gradually rumples or settles the sleeping nook;
- repeated window-watching leaves subtle sill/condensation/weather traces;
- repeated activity-corner use adds small paper/work marks;
- repeated inspection/handling can make a possession look deliberately staged or frequently handled.

Prefer one or two high-perceptual-value consequences over a broad new mechanics layer. The screen should help an observer infer *what Moss has been doing while they were away* without opening debug data or an activity feed.

Automated subjective/temporal visual-quality judging remains a known weak area. Treat it honestly; do not call a static metric a warmth/smoothness oracle.

## Later

Only after the software experience is compelling: preferences/routines, richer long-term identity, optional interaction/conversation, and hardware renderer experiments. Hardware must remain a renderer/client of the same host-owned creature and history.

## Checkpoint discipline

For each meaningful user-visible iteration: implement → test/evaluate → run/inspect → capture one deterministic development snapshot → update `STATUS.md` / history → commit → push attempt. Avoid snapshotting every small edit and never commit the live SQLite/event ledger. Git is product-development history, not a backup of Moss's living state.
