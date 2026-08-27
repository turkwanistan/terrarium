# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, and `MEMORY.md` before changing behavior or architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Gen17 Phase 0–2 remains the accepted architectural/runtime baseline: deterministic persistent host-owned world state, exact replay, disposable 800×480 renderer, autonomous behavior, persistent objects, and habitat wear.

The latest normal product checkpoint is **Temporal aftermath polish** (`history/2026-08-27-temporal-aftermath-polish.md`). Existing history-derived physical consequences now emerge progressively in the renderer, respond subtly to current weather, and use quieter visual hierarchy without changing canonical world behavior or authority boundaries.

Meaningful snapshot: `snapshots/dev/20260827T115103702156Z-temporal-aftermath-polish`.

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

`artifacts/visual-storytelling-comparison.json` and `artifacts/activity-aftermath-comparison.json` retain the earlier spatial/history comparisons. The latest `artifacts/temporal-aftermath-polish.json` proves the seed-1701/tick-240 semantic frame is unchanged while the renderer moved from seven discrete activity-stage rules to 26 progressively emerging authored aftermath layers with no `Math.random`.

## Self-Building Computer / memory state

The promoted reusable capability remains `simulation-behavior-auditor-r1`, content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`, evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae`.

It has now been reused again on the temporal-aftermath checkpoint (`cap_20260827T115050Z_933e3d93`) and passed on the matching 180-event deterministic stream. Candidate procedural memories remain non-authoritative; do not weaken applicability or promotion gates merely to activate them. See `MEMORY.md`.

Operational Optiplex_Lab remains accepted Gen6 with permanent MCP surface 10. Frozen Optiplex_MCP must not be modified.

## Highest-value next work

Make **present activity and accumulated aftermath feel causally connected in the renderer**: let the existing bedding, window traces, and activity-corner aftermath react subtly when Moss is currently using those spaces, without adding dashboards, routines, dialogue, or broad new mechanics.

## Git / remote safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed or copy credentials into the repository or bypass the credential boundary.
