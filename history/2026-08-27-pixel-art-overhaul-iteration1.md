# 2026-08-27 — Pixel-Art Overhaul, Iteration 1

## Decision

Accepted the first pixel-art lift-and-shift after Action Choreography, Composition, and Pacing. This remains normal Terrarium product development, not Self-Building Computer Gen18.

## Product change

The real browser renderer now authors at 400×240 and presents at 800×480 using exact 2× nearest-neighbor scaling with smoothing disabled. The semantic `TerrariumFrame` remains 800×480 and unchanged.

Moss was redesigned as a compact brown floppy-eared pixel dog with side/three-quarter gameplay poses, minimal face, planted legs, readable tail, no default glasses, and key-pose translations of the existing interaction language. The room, persistent objects, history marks, furniture overlaps, and environmental states were rebuilt from hard-edged pixel clusters and stepped palette families rather than gradients/smooth vector geometry.

## Semantic preservation

Accepted snapshot: `20260827T183924459328Z-pixel-art-overhaul-iteration1`, seed 1701 / tick 698. Frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c` exactly matches the accepted pre-overhaul tick-698 frame. Renderer SHA256 is `b2fc125fb72560fd8414850b26cf08cad31bd2f2ba7bab8792bffe9b7eccc0be`.

Pacing remains 3-second heartbeat, 1 world minute/heartbeat, 72-real-minute full day, ~9-real-minute deterministic weather blocks, and seed-1701/500 behavior at 186 decisions + 314 continuation ticks.

## Pixel pipeline evidence

Real-browser deterministic capture covered 16 scenarios / 176 sampled frames spanning idle/day, left/right locomotion, arrival settling, inspect, pickup, carry, place, sleep, wake, window, populated persistent history, activity corner, dawn, dusk/night, and rain. Every sample reported a 400×240 art surface, integer scale 2, smoothing disabled, exact 2× raster duplication, and zero mismatched 2×2 output blocks.

Repeated `left_walk` capture was byte-identical at SHA256 `dfe4612dbf9376a743c84893137f46f5e5e8b74c5a8eae263bac940f01ab1793`. Continuity interruption remained 0 px. Real RAF pacing: 16.6 ms minimum, 16.7 ms p50, 16.8 ms p95/max, zero >34 ms and zero >50 ms stalls.

## Auditor gap and specialization

The existing promoted `temporal-render-auditor-r1` was run unchanged first. All original defect classes stayed clean, but several valid grid-quantized sequences failed only `endpoint_settling`; on a 15-pixel pickup move the minimum visible 2-pixel art-grid step makes a subpixel-style endpoint-speed ratio intrinsically unsuitable.

This was a demonstrated reusable gap, so Capability Forge was used. The promoted specialization is `grid-quantized-temporal-render-auditor-r1`, content hash `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`, evaluator hash `3115517877e016d4b4867da15b3d5ef81045991d3bf890765c53dfdaa9a6782f`.

The specialization preserves every original check. Endpoint settling may use the renderer's continuous deterministic anchor only if each visible rendered point proves the declared integer-grid relationship (within half a grid cell). A false declaration fails `grid_quantization_contract`.

Evidence:

- original auditor oracle preserved: 10/10 expected classifications;
- Forge evaluation: 6/6;
- genuine Terrarium tasks: 2/2;
- current pixel sequence/probe set: 9/9;
- Gen14 dangerous mutants: 2/2 killed, kill rate 1.0, no survivors.

No new permanent MCP surface or SBC substrate work was required. No Gen18 warranted.

## Regression / UAT

- pytest 22/22 PASS;
- JavaScript syntax PASS;
- Python 3.10 compatibility PASS;
- technical evaluator PASS;
- exact replay hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator PASS with unchanged pacing/distribution baseline and all six objects moved;
- real 800×480 visual inspection accepted the pixel-native room, brown Moss, interaction readability, persistent history, day/dusk/night/rain coherence, and focal hierarchy.

Primary bounded evidence: `artifacts/pixel-art-overhaul-iteration1.json`. Raw browser sequences and Lab transport payloads are intentionally temporary.
