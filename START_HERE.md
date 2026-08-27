# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, and `MEMORY.md` before changing behavior or architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Gen17 Phase 0–2 remains the accepted architectural/runtime baseline: deterministic persistent host-owned world state, exact replay, disposable 800×480 renderer, autonomous behavior, persistent objects, and habitat wear.

The latest normal product checkpoint is **Present-world causality** (`history/2026-08-27-present-world-causality.md`). Current activity now visibly engages accumulated bedding/window/work-surface history, the canonical window contact point is physically aligned to the sill-side habitat, and object placement visibly settles rather than snapping. The simulation/event ledger remains authoritative.

Meaningful snapshot: `snapshots/dev/20260827T142112545745Z-present-world-causality` (seed 1701 / tick 97).

## Fresh-session procedure

1. Inspect `git status`, log, remote/tracking state, and active jobs/services; preserve unrelated work.
2. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `history/GEN17.md`, and the latest checkpoint history file.
3. Run `python -m pytest -q`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Inspect `artifacts/present-world-causality.json`, compact causal temporal evidence, the latest snapshot, and inherited replay evidence when validating persistence/replay claims.
6. Resolve reusable capabilities only after reading repository authority. `temporal-render-auditor-r1` is promoted at content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`. `simulation-behavior-auditor-r1` remains promoted for behavior analysis. Candidate procedural memory is never source authority.
7. For normal live viewing, prefer the canonical OptiPlex world via `./scripts/run_lan.sh`; the browser is disposable. For isolated development comparisons, use an ignored development data directory and never confuse it with canonical Moss.
8. Temporal development endpoints are disabled by default. Enable fixture/output flags only on a development service; never add those flags to canonical runtime launchers.
9. After a meaningful visible/product improvement: test/evaluate → run the actual renderer → visually inspect → capture exactly one meaningful deterministic development snapshot → update status/history → commit → attempt the mediated push.

## Current evidence

`artifacts/present-world-causality.json` is the compact checkpoint summary. `artifacts/causal-temporal-compact/` retains bounded genuine Canvas evidence; `artifacts/temporal-render-fixtures.json` retains deterministic source/target fixtures; larger raw browser sequences are intentionally discarded after compaction.

Current Canvas matrix: 10/10 deterministic scenarios PASS under the promoted temporal auditor plus real RAF PASS. Repeated raw deterministic `left_walk` SHA256: `518b7909af6c5c20e2573ee12f30923ca15faff4a1153954098137019c0d3a8a`. RAF: 109 intervals, max 16.8 ms, zero >50 ms stalls.

Separate deterministic telemetry—not an artistic score—proves sleep/window/activity-corner contact envelopes rise monotonically `0 → 1`, and the representative red-thread placement settles from `(118,372)` to `(181,400)` with zero final target error.

## Self-Building Computer state

Promoted temporal capability: `temporal-render-auditor-r1`, content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`.

Promoted behavior capability: `simulation-behavior-auditor-r1`, content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`.

No reusable SBC substrate deficiency was exposed; permanent Lab MCP surface remains 10. Frozen Optiplex_MCP must not be modified. No Gen18 is warranted by this checkpoint.

## Highest-value next work

Deepen **local action staging and object affordances**: clearer anticipation/contact/recovery around the specific nearby object or surface while Moss inspects, carries, places, looks out, or sleeps. Preserve the same world authority and use temporal checks for correctness, not subjective quality.

## Git / remote safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed or copy credentials into the repository or bypass the credential boundary.
