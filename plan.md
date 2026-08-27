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

## Evaluation loop

Keep the development loop: implement → deterministic accelerated run → technical/behavior evaluation → live browser inspection → identify weakness → bounded change → replay/regression.

Primary metrics: replay equality; event-chain integrity; restart equality; action diversity/entropy; non-sleep repetition; object pickups/placements/inspections; moved-object count; persistent habitat marks; renderer authority/synchronization; event storage growth.

## Next product iteration

Highest-value target: make persistent changes visually legible enough that reopening the display communicates "something happened while I was gone" without any dashboard text. Improve object staging/accumulation, creature transitions and animation timing, and richer environmental traces. Add stronger temporal/browser visual acceptance rather than declaring subjective quality from static code checks.

## Later

Only after the software experience is compelling: preferences/routines, richer long-term identity, optional interaction/conversation, and hardware renderer experiments. Hardware must remain a renderer/client of the same host-owned creature and history.
## Checkpoint discipline
For each meaningful user-visible iteration: implement -> test/evaluate -> run/inspect -> capture deterministic development snapshot -> update `STATUS.md` / history -> commit -> push. Avoid snapshotting every small code edit and never commit the live SQLite/event ledger. This makes the repository a useful chronological product record without turning it into a runtime backup.
