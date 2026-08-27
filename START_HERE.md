# START HERE

This repository is the authoritative Terrarium project created during Self-Building Computer Generation 17. Read `STATUS.md`, `plan.md`, and `terrarium.md` before changing behavior or architecture.

## Current checkpoint

Phase 0–2 initial scope is implemented and evaluated. The world is deterministic, persistent, event-sourced/snapshotted, renderer-independent, and capable of autonomous object/environment changes. The reference renderer is fixed at 800×480 logical pixels.

## Fresh-session procedure

1. Inspect `git status` and remote state; preserve unrelated work. Normal Terrarium development should commit/push only at meaningful tested checkpoints, unless the user says otherwise.
2. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, and `history/GEN17.md`. Repository/live evidence is authoritative over chat memory.
3. Run `python -m pytest -q`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Inspect `artifacts/gen17-live-replay.json`, `artifacts/gen17-technical-eval.json`, and `artifacts/gen17-behavior-eval.json`.
6. Search relevant Self-Building Computer procedural memory only after reading repository authority; validate applicability/hashes and never treat candidate memory as accepted truth.
7. For live visual work, start `python -m terrarium.api.server --data-dir data/live --seed 1701 --tick-seconds 1` and inspect the browser renderer. Treat the world process as authority, never the browser.
8. After a meaningful visible/product improvement, capture a deterministic dev snapshot (`tools/capture_dev_snapshot.py`), inspect `/snapshots/`, update status/history, then commit/push the tested checkpoint.

## Gen17 builder evidence

The Gen16 project-factory path classified the project capabilities with required-evidence recall 1.0 / critical FN 0. A real missing capability, `simulation-behavior-auditor-r1`, was forged, independently evaluated, used twice on Terrarium, mutation-tested, and promoted by the existing governor. Its content hash is `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`.

A project-driven Lab defect was also found: Capability Forge required JSON Schema Draft 2020-12 but the guest had `jsonschema 3.2.0`. The guest-local dependency was repaired to `jsonschema 4.23.0`; Forge selftest returned 8/8 and Gen16 regression returned 40/40 afterward. Permanent MCP surface remains 10 tools and the operational Gen6 server/LKG is unchanged.

## Highest-value next work

Improve the feeling that activity happened while the viewer was away: strengthen visual storytelling of persistent object movement/accumulation and temporal animation quality, then add stronger browser/temporal visual acceptance evidence. Do not jump to learned preferences, conversation, or hardware merely for breadth.

## Git / remote safety
The local repository has real checkpoint history and `origin` points to `git@github.com:turkwanistan/terrarium.git`. The first mediated push was blocked because credentials were not provisioned for this new project. Do not embed tokens, keys, or copied SSH credentials. Once the GitHub repository/project authorization exists, use the mediated project push path at each meaningful tested checkpoint.
