# Pixel-Art Overhaul — Iteration 2: Sprite Acting and Environmental Detail

Accepted 2026-08-27 as a normal Terrarium product checkpoint, not Self-Building Computer Generation 18.

## Product change

Iteration 1 proved the native 400×240 pixel-art surface and rebuilt the world into a consistent pixel language. Iteration 2 concentrated on authored acting and illustrated depth.

Moss now uses discrete authored key-pose grammar rather than a generic body plus procedural deformation: a four-frame walk with planted/opposing contacts and ear/tail response; target-facing inspect; staged pickup anticipation/contact/attachment/recovery; stable carry posture; staged place contact/release/recovery; window gaze/settle; rest; multi-stage sleep curl; and multi-stage wake unfold. Renderer posture remains subordinate to canonical action/target/state authority.

The room received deeper construction and material hierarchy: inset window casing, curtain folds, sill/supports, structured bed/blanket/pillow/footboard, woven rug border, recessed shelf bays/lips/books/trinkets, desk planes/apron/legs/drawer, stepped bowls, sparse plaster irregularity, floor boards/grain, furniture feet, contact shadows, and stronger foreground/midground overlaps. Persistent bedding/window/activity/path/object history remains derived only from authoritative frame state.

Lighting and weather remain discrete palette/cluster changes. Rain was made sparser and more window-localized; ambient motes were slowed. No gradients, blur, random jitter, high-resolution pixelation pass, or semantic renderer authority was introduced.

## Objective evidence

- semantic seed/tick 1701/698 remains SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`, identical to Iteration 1;
- renderer JS SHA256 `7b03f5554d121fa8dec5481e8078547baac3f28589968a4da9570b3a0925e0e6`;
- pytest 22/22 PASS, including Python 3.10 grammar guard;
- JavaScript syntax PASS;
- technical evaluator PASS; exact replay canonical/replayed hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator seed 1701 / 500 PASS with 186 new decisions + 314 continuation ticks and all six objects moved;
- 17 deterministic real-browser scenarios / 187 sampled frames all satisfy exact 400×240 → 800×480 2× duplication, smoothing off, zero scale-error blocks;
- all four authored walk keyframes observed;
- repeated left-walk capture byte-identical SHA256 `95a2f2c0f7bb551023ff0852302e316cb5d10403ea7b97f1489e9b0395348ddf`;
- continuity probe 0 px jump;
- real RAF 16.5/16.7/16.8/16.8 ms min/p50/p95/max, zero >34 ms and >50 ms stalls;
- existing promoted `grid-quantized-temporal-render-auditor-r1` 9/9 PASS with zero grid-contract mismatches;
- representative walk, pickup/contact, sleep curl, rain-window, populated-history, and dusk scenes inspected in the actual 800×480 browser Canvas.

The first pytest invocation was accidentally executed through the read-only MCP project sandbox and failed only because the snapshot smoke test could not create its temporary fixture under `/workspace/snapshots/dev`. The same suite was immediately rerun with project write permission and passed 22/22; the generated pytest-smoke snapshot was deleted and is not a development checkpoint.

## Snapshot

Accepted snapshot: `20260827T192116263284Z-pixel-art-overhaul-iteration2`.

It records the unchanged semantic frame and new renderer identity with art-surface contract 400×240, integer scale 2, smoothing false.

## SBC conclusion

The existing deterministic capture stack and promoted grid-quantized temporal specialization covered every exposed objective risk. No evaluator change, Forge run, new capability, platform modification, permanent MCP growth, or SBC generation was needed. **No Gen18 warranted.**
