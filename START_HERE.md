# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `ART_DIRECTION.md`, and the latest history checkpoint before changing behavior or renderer architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Latest normal product checkpoint: **Visual maturity: art direction + motion coherence** (`history/2026-08-27-visual-maturity.md`).

Meaningful snapshot: `snapshots/dev/20260827T165449319827Z-visual-maturity` — deterministic seed 1701 / tick 180; frame SHA256 `9a422b0de25ffa7311a1b86e315379189ae485485edc79bc02e948d0959a1487`; renderer SHA256 `a523186cab91e614034eb6593e3ea3db4b558ac448ca5d1c640cd43fb7362807`.

The reference renderer now follows `ART_DIRECTION.md`: cozy low-resolution storybook diorama, Moss-first focal hierarchy, governed material/palette/depth language, primary→secondary→ambient motion hierarchy, and anticipation→movement→contact→settle→recovery action grammar.

## Fresh-session procedure

1. Inspect `git status`, log, remote/tracking state, and active jobs/services; preserve unrelated work.
2. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `ART_DIRECTION.md`, `history/GEN17.md`, and `history/2026-08-27-visual-maturity.md`.
3. Run `python -m pytest -q`.
4. Run `node --check display/web/app.js`, `python evaluations/evaluate_technical.py`, and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Inspect `artifacts/visual-maturity.json`, compact genuine Canvas evidence under `artifacts/visual-maturity-compact/`, the latest snapshot, and inherited replay evidence when validating persistence/replay claims.
6. Resolve reusable capabilities only after reading repository authority. `temporal-render-auditor-r1` is promoted at content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`. `simulation-behavior-auditor-r1` is promoted at content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`. Candidate procedural memory is never source authority.
7. For normal live viewing, prefer the canonical OptiPlex world via `./scripts/run_lan.sh`; the browser is disposable. For isolated development comparisons, use a temporary/ignored data directory and never confuse it with canonical Moss.
8. Temporal development endpoints are disabled by default. Enable fixture/output flags only on a development service; never add those flags to canonical runtime launchers.
9. Use objective temporal checks for teleport/jitter/facing/attachment/settling/RAF correctness, **not** for aesthetic scoring. Visually inspect the actual 800×480 Canvas for warmth, composition, readability, and art-direction coherence.
10. After a meaningful visible/product improvement: test/evaluate → run actual renderer → visually inspect → capture exactly one meaningful deterministic development snapshot → update status/history → create one meaningful commit → attempt the mediated push.

## Current evidence

`artifacts/visual-maturity.json` is the primary compact checkpoint summary. `artifacts/visual-maturity-compact/` retains bounded real Canvas telemetry/raster evidence; larger raw browser sequences and Lab transports were intentionally discarded after compaction. `artifacts/temporal-render-fixtures.json` retains deterministic source/target fixtures.

Current temporal matrix: **15 deterministic hero sequences plus real RAF = 16/16 PASS** under the promoted temporal auditor in isolated Lab. A separate consecutive-update probe proves the principal live defect improved from `352.907594 px` instantaneous legacy jump to `0 px`. Repeated deterministic `left_walk` raw capture SHA256 is `8853ad450bb5cac36ea5273b24de069b8ec9656ede77d7787574d1b7063992d5`. RAF: 156 intervals, median 16.7 ms, max 16.8 ms, zero >50 ms stalls.

Current seed-1701/500 behavior remains diverse but visually calmer: 10 action classes, entropy `3.103385`, 19 consecutive movement pairs, 5 immediate zone reversals, max movement burst 2, 97 configured object interactions under the promoted behavior auditor.

## Self-Building Computer state

No new capability was required for this checkpoint. Existing promoted temporal and simulation behavior auditors, isolated Lab, browser mediation, deterministic evidence, exact replay, and snapshots were sufficient. Permanent Lab MCP surface did not grow. Frozen Optiplex_MCP must not be modified.

**No Gen18 warranted.**

## Highest-value next work

Continue normal product work under the art bible. Prefer a few high-impact authored interaction/composition improvements over feature count, effects, or new action types. Any future simulation change must remain deterministic, authoritative on the host, and behavior-regression-tested rather than hidden in JavaScript.

## Git / runtime safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed/copy credentials into the repository or bypass the credential boundary. A development service is not a canonical LAN deployment; report a LAN URL only after actual host-owned runtime verification.
