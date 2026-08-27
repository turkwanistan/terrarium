# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul, Iteration 1**. This is **not Generation 18**.

## Current checkpoint

Latest product checkpoint: **Pixel-Art Overhaul, Iteration 1** (`history/2026-08-27-pixel-art-overhaul-iteration1.md`).

Meaningful snapshot: `20260827T183924459328Z-pixel-art-overhaul-iteration1` — deterministic seed **1701**, tick **698**; frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`; renderer SHA256 `b2fc125fb72560fd8414850b26cf08cad31bd2f2ba7bab8792bffe9b7eccc0be`.

The tick-698 semantic frame hash is byte-for-byte identical to the accepted pre-overhaul snapshot. The overhaul changed presentation, not the authoritative world, behavior engine, object layout, or pacing.

Primary bounded evidence: `artifacts/pixel-art-overhaul-iteration1.json`.

## Pixel-native renderer

The renderer now authors the scene on a true **400×240 internal Canvas** and presents it at the fixed **800×480** reference size through exact **2× nearest-neighbor scaling**.

- internal art surface: **400×240**;
- external/reference surface: **800×480**;
- scale: exact integer **2×**;
- smoothing: disabled internally and at presentation;
- semantic 800-space coordinates remain canonical; presentation snaps them at the art-grid boundary;
- no high-resolution art is rendered and pixelated afterward;
- no gradients, ellipse-based smooth painting, rounded vector geometry, blur, bloom, or random camera effects remain in the primary Canvas art path.

Real-browser raster telemetry covered **16 deterministic scenarios / 176 sampled frames**. Every sampled 800×480 frame was exact 2×2 pixel duplication from the 400×240 art surface with **0 mismatched scale blocks**.

## Art direction

`ART_DIRECTION.md` is now the pixel-art bible. The target is handcrafted late-16-bit/early-32-bit farming/life-RPG pixel art with moderately chunky clusters, 2–4 stepped shades, selective outlines, sparse hard-edged shadows, and a warm moss/walnut/amber/dusty-blue/cream palette.

Moss is now a small **brown floppy-eared dog sprite** with a compact body, slightly oversized head, short planted legs, readable tail, minimal face, and side/three-quarter gameplay orientation. The default hero sprite has **no glasses**. Idle, locomotion, inspect/contact, pickup, carry, place, sleep, wake, and window-watching poses are represented through pixel-native key-pose logic.

The room was rebuilt in the same language: warm wood interior, moss-green open rug, window/curtains, shelf/books, sleeping nook, bowls, plant, activity desk, persistent objects, foreground overlaps, and accumulated causal history. Path wear, object scuffs, bedding history, window traces, and activity aftermath remain driven by canonical state.

Day/dawn/dusk/night and rain/mist now use finite palette/value shifts and sparse pixel effects rather than smooth volumetric lighting.

Human inspection of the real Canvas remains the aesthetic authority; no beauty score was added.

## Pacing and choreography preserved

Accepted pacing did not change:

- heartbeat: **3 real seconds**;
- world advance: **1 world minute / heartbeat**;
- full day: **72 real minutes**;
- deterministic weather block: approximately **9 real minutes**;
- seed 1701 / 500 heartbeats: **186 new decisions + 314 continuation ticks**;
- continuation ticks do not restart action animation clocks.

Canonical target ownership and interaction order remain intact: contact before attachment, stable carried-object attachment, place contact/release/settle, supported sleep, and renderer-only posture around authoritative targets.

## Temporal auditor specialization

The promoted `temporal-render-auditor-r1` was run unchanged first. It preserved all important defect checks but rejected several valid pixel-native sequences only on `endpoint_settling`: a 2-pixel presentation quantum can make a short valid transition's first/last visible step appear too fast relative to peak motion even when the underlying trajectory settles correctly.

This demonstrated a reusable capability gap. Existing SBC mechanisms—not a new generation—were used to forge `grid-quantized-temporal-render-auditor-r1`:

- content hash: `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`;
- Forge evaluator hash: `3115517877e016d4b4867da15b3d5ef81045991d3bf890765c53dfdaa9a6782f`;
- state: **PROMOTED**;
- Forge evaluation: **6/6 PASS**;
- real Terrarium tasks: **2/2 PASS**;
- original temporal oracle classifications preserved: **10/10**;
- current pixel audit set: **9/9 PASS**, including RAF;
- Gen14 dangerous mutations killed: **2/2**, kill rate **1.0**, survivors **0**.

The specialization does not waive endpoint settling. It may evaluate endpoint speed from the renderer's deterministic continuous presentation anchor only when each visible rendered coordinate also proves it lies within half of the declared integer grid cell. False grid declarations fail closed under `grid_quantization_contract`. Teleport, reversal, frozen motion, facing, scene jitter, attachment, causality, and RAF gates are unchanged.

## Objective regression

- pytest: **22/22 PASS**;
- JavaScript syntax: **PASS**;
- Python 3.10 compatibility: **PASS** through the existing grammar guard;
- technical evaluator: **PASS**;
- exact replay: **PASS**, canonical/replayed hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator seed 1701 / 500: **PASS**, 186 decisions + 314 continuation ticks, all 6 objects moved;
- behavior engine changed: **no**; promoted behavior-auditor rerun therefore not required by checkpoint policy;
- deterministic repeated `left_walk` browser capture: byte-identical SHA256 `dfe4612dbf9376a743c84893137f46f5e5e8b74c5a8eae263bac940f01ab1793`;
- continuity interruption jump: **0 px**;
- real RAF: min **16.6 ms**, p50 **16.7 ms**, p95/max **16.8 ms**, zero >34 ms and zero >50 ms stalls;
- real 800×480 UAT: **accepted**.

## SBC conclusion

A real reusable auditor gap was found and absorbed by existing Capability Forge + Gen14 mutation/isolation machinery. No permanent MCP surface changed, the SBC substrate itself did not require modification, and **Gen18 is not warranted**.

## Runtime / remote safety

Canonical Moss state remains outside Git in the user-owned runtime directory. All development/evaluation services used disposable state. Never substitute a temporary world for the canonical deployment.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated safe push path. Update the canonical OptiPlex deployment only through its established launcher/owner and report a LAN URL only after verifying that host-owned runtime.

## Highest-value next product work

Use human UAT of this first pixel-art lift-and-shift to choose **Pixel-Art Overhaul, Iteration 2** targets. Favor visible craft: Moss silhouette/pose refinement, furniture/tile cluster polish, room composition, environmental palette nuance, and interaction readability. Do not expand mechanics merely to fill the scene, and do not weaken the grid-aware temporal gate to accommodate bad animation.
