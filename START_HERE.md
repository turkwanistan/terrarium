# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, and `MEMORY.md` before changing behavior or architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Gen17 Phase 0–2 remains the accepted architectural/runtime baseline: deterministic persistent host-owned world state, exact replay, disposable 800×480 renderer, autonomous behavior, persistent objects, and habitat wear.

The latest normal product checkpoint is **Activity aftermath** (`history/2026-08-27-activity-aftermath.md`). Repeated window-watching, activity-corner use, and sleeping-nook sleep now leave distinct deterministic physical consequences, while canonical runtime architecture and authority boundaries remain unchanged.

Meaningful snapshot: `snapshots/dev/20260827T054359565518Z-activity-aftermath`.

## Fresh-session procedure

1. Inspect `git status`, log, remote/tracking state, and active jobs/services; preserve unrelated work.
2. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `history/GEN17.md`, and the latest checkpoint history file.
3. Run `python -m pytest -q`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Inspect the latest checkpoint artifacts plus `artifacts/gen17-live-replay.json` when validating inherited persistence/replay claims.
6. Search relevant Self-Building Computer procedural memory only after reading repository authority; validate applicability/preconditions and capability/evaluator hashes. Candidate memory is never source authority.
7. For normal live viewing, prefer the canonical OptiPlex world via `./scripts/run_lan.sh`; the browser is disposable. For isolated development comparisons, use an ignored development data directory and never confuse it with canonical Moss.
8. After a meaningful visible/product improvement: test/evaluate → run the actual renderer → visually inspect → capture one deterministic development snapshot → update status/history → commit → attempt the mediated push.

## Current visual-storytelling evidence

`artifacts/visual-storytelling-comparison.json` compares fresh tick 0, the accepted Gen17 tick-240 baseline, and improved tick-720 accelerated life. `artifacts/visual-storytelling-counterfactual.json` holds a same-seed/same-horizon comparison against Gen17 commit `0fa3952`; old Gen17 overlaps two shelf-object pairs at tick 720, while the current implementation gives all six placed objects distinct authored coordinates with the same shelf count and path wear.

## Self-Building Computer / memory state

The promoted reusable capability remains `simulation-behavior-auditor-r1`, content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`, evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae`.

It was genuinely reused on the lived-in-staging checkpoint and passed. That real reuse was recorded, but memory activation remained fail-closed because the recorded held-out episode omitted the required `input_schema_hash` environment precondition. See `MEMORY.md`; do not weaken that gate or treat either memory object as active authority.

Operational Optiplex_Lab remains accepted Gen6 with permanent MCP surface 10. Frozen Optiplex_MCP must not be modified.

## Highest-value next work

Polish **temporal readability of the new activity aftermath**: keep the cues physical and history-derived, but make threshold transitions and subtle animation feel natural without adding dashboards or unrelated mechanics.

## Git / remote safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed or copy credentials into the repository or bypass the credential boundary.
