# START HERE

This repository is the authoritative Terrarium project created during the accepted Self-Building Computer Generation 17 pilot and now developed as a normal product. Read `STATUS.md`, `plan.md`, `terrarium.md`, `MEMORY.md`, `ART_DIRECTION.md`, and the latest history checkpoint before changing behavior or renderer architecture. Do not invent a new SBC generation merely because a Terrarium checkpoint completes.

## Current checkpoint

Latest checkpoint: **Pixel-Art Overhaul, Iteration 1** (`history/2026-08-27-pixel-art-overhaul-iteration1.md`).

Accepted snapshot: `snapshots/dev/20260827T183924459328Z-pixel-art-overhaul-iteration1` — seed **1701** / tick **698**; frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`; renderer SHA256 `b2fc125fb72560fd8414850b26cf08cad31bd2f2ba7bab8792bffe9b7eccc0be`.

The semantic frame is identical to the pre-overhaul accepted tick-698 frame. The visual architecture changed; canonical state did not.

## Renderer authority

The real renderer is now pixel-native:

- authoritative semantic contract remains fixed 800×480 `TerrariumFrame`;
- presentation art surface is **400×240**;
- final output is exact **2× nearest-neighbor** to **800×480**;
- smoothing/subpixel art placement is prohibited;
- the renderer may quantize presentation but may not own targets, behavior, history, time, or object state.

`ART_DIRECTION.md` is the visual bible. Moss is a brown floppy-eared gameplay sprite with no default glasses; the room and persistent history use the same clustered pixel language.

## Pacing authority

Do not restore one-new-decision-per-heartbeat behavior or the old nine-minute day.

- heartbeat: **3 seconds**;
- world advance: **1 world minute / heartbeat**;
- day: **72 real minutes**;
- weather block: approximately **9 real minutes**;
- seed 1701 / 500: **186 decisions + 314 continuation ticks**;
- continuation ticks preserve the current animation/action clock.

## Promoted objective capabilities

Resolve by exact identity when relevant:

- `simulation-behavior-auditor-r1` — `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`;
- `temporal-render-auditor-r1` — `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`;
- `grid-quantized-temporal-render-auditor-r1` — `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`.

Use the original temporal auditor for ordinary smooth rendering evidence. Use the grid specialization when the renderer explicitly declares integer-grid quantization and supplies continuous presentation anchors. The specialization still runs the original dangerous defect classes and fails closed if the grid contract is false.

Neither temporal capability is an aesthetic oracle.

## Fresh-session procedure

1. Inspect Git status/log/tracking and active services; preserve unrelated work.
2. Read `STATUS.md`, `ART_DIRECTION.md`, `MEMORY.md`, `history/GEN17.md`, and `history/2026-08-27-pixel-art-overhaul-iteration1.md`.
3. Run `python -m pytest -q` and `node --check display/web/app.js`.
4. Run `python evaluations/evaluate_technical.py` and `python evaluations/evaluate_behavior.py --seed 1701 --steps 500`.
5. Keep Python 3.10 syntax compatibility intact.
6. Inspect `artifacts/pixel-art-overhaul-iteration1.json`, the accepted snapshot, and `artifacts/temporal-render-fixtures.json` before changing rendering/timing behavior.
7. Preserve 400×240 → 800×480 exact 2× nearest-neighbor output; verify the real browser raster, not only source text.
8. If behavior changes, run the promoted behavior auditor. If temporal presentation changes, run the appropriate promoted temporal auditor plus real RAF pacing.
9. Visually inspect the actual 800×480 Canvas. Human judgment owns charm, composition, material coherence, Moss's personality, and whether the art truly reads as handcrafted pixels.
10. After one meaningful visible improvement: evaluate → real renderer UAT → exactly one snapshot → bounded evidence/docs/history → one commit → mediated push attempt → canonical host deployment verification.

## Current accepted evidence

`artifacts/pixel-art-overhaul-iteration1.json` records:

- 16 deterministic browser scenarios / 176 sampled frames with exact 2× raster duplication and 0 scale errors;
- pytest **22/22 PASS**;
- exact replay hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- unchanged seed-1701/500 behavior pacing (**186 + 314**);
- deterministic capture repeat SHA `dfe4612dbf9376a743c84893137f46f5e5e8b74c5a8eae263bac940f01ab1793`;
- continuity jump **0 px**;
- real RAF max **16.8 ms**, zero stalls;
- grid-aware auditor promotion/evaluation/mutation evidence;
- real Canvas UAT accepted.

Large raw browser/Lab transport evidence is temporary and should not be retained once the bounded artifact exists.

## SBC conclusion

This iteration demonstrated one reusable capability gap and forged a bounded specialization through existing SBC mechanisms. No SBC substrate change or permanent MCP growth was needed. **No Gen18 warranted.**

## Runtime / Git safety

Canonical Moss state is user-owned and lives outside Git. Development services use disposable state. Never overwrite or replace the living world with a test world.

Use the mediated safe push path. Restart/update the canonical OptiPlex runtime only through the established launcher/owner, preserving its existing state directory. Report a LAN URL only after the canonical service is verified.
