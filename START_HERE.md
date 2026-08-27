# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, and `MEMORY.md` before changing behavior or architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Gen17 Phase 0–2 remains the accepted architectural/runtime baseline: deterministic persistent host-owned world state, exact replay, disposable 800×480 renderer, autonomous behavior, persistent objects, and habitat wear.

The latest normal product checkpoint is **Temporal rendering intelligence** (`history/2026-08-27-temporal-rendering-intelligence.md`). Terrarium can now deterministically drive the actual Canvas renderer at exact timestamps, record compact motion/raster evidence, separately measure real RAF pacing, and objectively detect major temporal correctness regressions without treating automated metrics as a warmth/charm oracle.

Meaningful snapshot: `snapshots/dev/20260827T125248568567Z-temporal-rendering-intelligence`.

## Fresh-session procedure

1. Inspect `git status`, log, remote/tracking state, and active jobs/services; preserve unrelated work.
2. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `history/GEN17.md`, and the latest checkpoint history file.
3. Run `python -m pytest -q`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Inspect `artifacts/temporal-rendering-intelligence.json`, compact temporal audit inputs, the latest snapshot, and `artifacts/gen17-live-replay.json` when validating inherited persistence/replay claims.
6. Resolve reusable capabilities only after reading repository authority. `temporal-render-auditor-r1` is promoted at content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`. `simulation-behavior-auditor-r1` remains promoted for behavior analysis. Candidate procedural memory is never source authority.
7. For normal live viewing, prefer the canonical OptiPlex world via `./scripts/run_lan.sh`; the browser is disposable. For isolated development comparisons, use an ignored development data directory and never confuse it with canonical Moss.
8. Temporal development endpoints are disabled by default. Enable fixture/output flags only on a development service; never add those flags to canonical runtime launchers.
9. After a meaningful visible/product improvement: test/evaluate → run the actual renderer → visually inspect → capture one deterministic development snapshot → update status/history → commit → attempt the mediated push.

## Current temporal evidence

`artifacts/temporal-rendering-intelligence.json` is the compact checkpoint summary. `artifacts/temporal-audit-inputs/` retains bounded genuine Canvas task evidence; `artifacts/temporal-render-fixtures.json` retains deterministic source/target fixtures; `artifacts/temporal-lab-transport.json` records the bounded Lab handoff; and `artifacts/temporal-capability-gap.json` records the project capability gap. Larger raw browser sequences were intentionally discarded after compaction.

Repeated deterministic left-walk capture SHA256: `f204f15e6ba50e1126642aca3761795a64954f799d7141c5ff0a1b126d15b410`. Real RAF control: 110 frames / 1816.6 ms, 16.7 ms p50/p95, 16.8 ms max, no >34 ms gaps.

## Self-Building Computer state

Promoted temporal capability: `temporal-render-auditor-r1`, content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`.

Gen14 mutation evidence killed 10/10 dangerous mutants with zero survivors and accepted state unchanged. No reusable SBC substrate deficiency was exposed; permanent Lab MCP surface remains 10. Frozen Optiplex_MCP must not be modified.

## Highest-value next work

Use temporal proof to make **present activity and accumulated aftermath feel causally connected**. Let existing bedding, window traces, and activity-corner aftermath react subtly while Moss is currently using those spaces; retain the same authority boundaries and use objective temporal checks only for correctness, not artistic taste.

## Git / remote safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed or copy credentials into the repository or bypass the credential boundary.
