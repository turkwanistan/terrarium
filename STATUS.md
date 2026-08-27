# Terrarium Status

Checkpoint: **GEN17 INITIAL SCOPE ACCEPTED** (Phase 0–2 initial pilot).

## Product
- Fixed logical renderer: **800×480**.
- Canonical creature/world state is outside the renderer in SQLite + append-only event history.
- Browser close/reopen proof: authoritative tick/event advanced **36 → 63** while the Terrarium tab was closed.
- Process restart proof: a new world process resumed existing state, reaching tick/event **87** rather than resetting.
- Stopped final live proof: **402 events/ticks**, exact replay PASS, canonical/replayed hash `b3d10eda99f8b3ba580043d4d7c40bd1ce0cde0f9cbc45cde019fb3d1fc21a1b`.
- Autonomous vocabulary includes idle, walk, explore, rest, sleep/wake, inspect, carry, place, and look outside.
- Persistent objects and habitat wear survive restart/replay.
- Browser renderer reopened cleanly after process restart; no renderer-owned history/state.

## Final project evaluation
- pytest: PASS.
- technical evaluator: PASS; 80 events; exact replay; append-only SQLite enforcement; event hash chain; fixed viewport; restart persistence.
- behavior evaluator: PASS at seed 1701 / 500 steps; 10 action classes; entropy 3.151553 bits; 28 placements; 28 pickups; 58 inspections; all 6 objects moved; 10 persistent habitat marks.
- compact event redesign reduced the observed 100-event JSONL footprint from ~889 KB to ~124 KB while preserving deterministic replay.

## Self-Building Computer / capability evidence
- Gen16 consolidated onboarding path exercised on Terrarium: required-evidence recall **1.0**, critical FN **0**.
- Initial gap: `simulation-behavior-auditor` = `MISSING_VALUABLE`.
- Retained capability: `simulation-behavior-auditor-r1`, content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`, state `PROMOTED` only after 3/3 Forge evaluation + 2 successful Terrarium real tasks + governor gate.
- Dangerous sequence-integrity fail-open mutant: **KILLED**, mutation kill rate 1.0, accepted state unchanged.
- Lab defect exposed/fixed: guest `jsonschema 3.2.0` lacked Draft-2020-12; repaired to `4.23.0`; Forge selftest 8/8 PASS afterward.
- Post-change Gen16 protection benchmark: **40/40 PASS**.
- Operational Lab remains Gen6 server/LKG `dc0d2cb41595a9a3d953873879ccc3e0bd88db2b4dcdee4cf8aa43dd4cb103e9`, recovery ACCEPTED, permanent tools 10, containment PASS.

## Known weakness / next iteration
Automated subjective temporal visual evaluation is still weak. Browser rendering/inspection works, but there is no proven oracle for animation smoothness, warmth, or "cozy diorama" quality. Improve persistent visual storytelling and temporal animation, then evaluate it with stronger visual/browser evidence. Hardware, learned preferences/routines, and conversation remain later phases.

No commit or push has been performed.
## Development-history policy
- milestone snapshots live under `snapshots/dev/`; default comparison scene is deterministic seed 1701 / step 240
- local gallery: `/snapshots/`; exact historical renderer identity is pinned by Git + renderer SHA
- Windows local launch: `scripts/run_windows.ps1`
- runtime `data/live/` is intentionally not version controlled
- target remote: `git@github.com:turkwanistan/terrarium.git`
- procedural memory policy: `MEMORY.md`; Gen17 behavior-auditor memory is intentionally CANDIDATE pending held-out/reuse evidence
- normal development should create one tested commit/push per meaningful checkpoint, with a snapshot when user-visible behavior/visuals change

## Repository bootstrap status
- local root commit: `c4b5377` (`Establish Terrarium Gen17 baseline and progressive snapshots`)
- `origin`: `git@github.com:turkwanistan/terrarium.git`
- first mediated push attempt: **blocked because project-specific Git push credentials are not yet provisioned for this new repository**
- do not copy credentials into the repo or bypass the mediated push boundary; create/authorize the GitHub repository once, then use normal checkpoint pushes
