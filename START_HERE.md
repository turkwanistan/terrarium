# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `ART_DIRECTION.md`, and the latest history checkpoint before changing behavior or renderer architecture. Do not invent a new Self-Building Computer generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Latest normal product checkpoint: **Action choreography, composition, and pacing** (`history/2026-08-27-action-choreography-pacing.md`).

Meaningful snapshot: `snapshots/dev/20260827T175337017716Z-action-choreography-pacing` — deterministic seed **1701** / tick **698**; frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`; renderer SHA256 `17feafe5e5c0c6327df0bef5aa00f5617847949dbd0e23e41516a37240f8a61a`.

At the accepted frame Moss is inspecting `amber_leaf` at the collection shelf during dusk, after all six objects have moved and seven persistent marks have accumulated. The frame was inspected through the real fixed 800×480 Canvas renderer.

## Pacing authority

Do not accidentally restore one-new-decision-per-tick behavior or the former nine-minute day.

- runtime heartbeat: **3 real seconds**;
- world advance: **1 world minute per heartbeat**;
- full day: **72 real minutes**;
- dawn/day/dusk/night: approximately **6 / 28.5 / 6 / 31.5 real minutes**;
- deterministic weather block: approximately **9 real minutes**;
- behavior decisions are separated from heartbeat advancement by canonical deterministic action commitments;
- seed 1701 / 500 heartbeats currently yields **186 decisions + 314 continuation/settle ticks**, about one new decision every **8.06 seconds** on average;
- renderer interpolation is faster and presentation-only; continuation frames do not restart the action clock.

Current commitment windows are about 6 seconds for idle/walk/explore/carry/place/wake, 9 seconds for rest/inspect, 12 seconds for window watching, and 15 seconds for sleep.

## Current interaction model

Canonical frame/event metadata owns targets. The renderer may stage posture around that metadata but may not invent behavior authority.

- inspect uses near-target stance, orientation, gaze/head/paw lean, hold and recovery;
- pickup establishes contact before transferring the object into a rigid paw/chest hold;
- carry preserves visible attachment and a steadier posture;
- place stops, lowers to the authoritative destination, contacts, releases, settles and retracts;
- window watching is planted and quiet;
- sleep/wake use supported nook poses and deliberate transitions;
- shelf/desk/blanket foreground edges provide intentional depth and occlusion.

`ART_DIRECTION.md` remains the visual authority. It already contains the reusable contact/depth/motion grammar needed by this checkpoint and was not changed.

## Fresh-session procedure

1. Inspect Git status/log/tracking and active services; preserve unrelated work.
2. Read `STATUS.md`, `MEMORY.md`, `ART_DIRECTION.md`, `history/GEN17.md`, and `history/2026-08-27-action-choreography-pacing.md`.
3. Run `python -m pytest -q` and `node --check display/web/app.js`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Keep source Python-3.10-syntax compatible; `tests/test_python_compat.py`/3.10 grammar validation is a required runtime guardrail.
6. Inspect `artifacts/action-choreography-pacing.json`, the latest snapshot, and deterministic `artifacts/temporal-render-fixtures.json` before changing pacing/renderer behavior.
7. Resolve promoted capabilities by exact hash when objective temporal or behavior regression is relevant: `temporal-render-auditor-r1` at `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`; `simulation-behavior-auditor-r1` at `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`.
8. For normal live viewing, use the established canonical OptiPlex launcher/deployment path and existing user-owned state directory. Development services use disposable state and are never the canonical Moss world.
9. Objective temporal checks cover teleport/jitter/facing/attachment/settling/RAF correctness. They are **not** aesthetic scoring. Visually inspect the real 800×480 Canvas for composition, warmth, personality and readability.
10. After a meaningful visible improvement: test/evaluate → real renderer visual review → exactly one meaningful snapshot → status/history/evidence → one commit → mediated push attempt → safe canonical deployment verification.

## Accepted evidence

`artifacts/action-choreography-pacing.json` is the bounded primary artifact. Current accepted evidence includes:

- pytest **20/20 PASS**;
- exact replay PASS at hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator PASS at seed 1701 / 500;
- promoted behavior auditor PASS: 186 decisions, 10 classes, entropy `3.165646`, 52 object interactions, sequence integrity;
- promoted temporal auditor PASS after fixing its initially detected defects; pickup/place settle ratio `0.04986`, sleep `0.095074` with zero facing mismatches, carried attachment span 0;
- continuity probe **0 px**;
- real RAF max **16.8 ms**, zero >50 ms stalls;
- repeated deterministic `left_walk` capture byte-identical at SHA256 `c25fa97c9870a5bc476f45f38ce2683b7fc9b0503e3675d3a9500688cb9a5a9f`;
- real hero-scene and accepted-snapshot visual review completed.

Large raw browser sequences and Lab transport payloads are temporary evidence only and should not be retained in Git once the bounded artifact is complete.

## Self-Building Computer state

Existing promoted behavior/temporal auditors, isolated Lab, browser mediation, deterministic evidence and project-safe lifecycle were sufficient. No capability was forged and permanent MCP surface did not grow. Frozen Optiplex_MCP must not be modified.

**No Gen18 warranted.**

## Git / runtime safety

Canonical runtime state lives outside Git under the user-owned Terrarium state directory. Never commit SQLite/WAL/SHM files or runtime event ledgers. Development snapshots are intentionally versioned product history.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path when authorized. Do not embed/copy credentials into the repository or bypass the credential boundary. Report a LAN URL only after the actual canonical host-owned runtime is verified.
