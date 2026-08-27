# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current checkpoint is **Pixel-Art Overhaul — Iteration 3: Spatial Coherence and Physical Acting**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-27-pixel-art-overhaul-iteration3.md`
- bounded evidence: `artifacts/pixel-art-overhaul-iteration3.json`
- accepted snapshot: `20260827T204232352544Z-pixel-art-overhaul-iteration3`
- deterministic seed/tick: **1701 / 698**
- semantic frame SHA256: `fe7ffd8dbefc56144c7af673a810339f136ae6f08db580cf80bc8b819f0996a9`
- renderer JS SHA256: `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`
- spatial schema: `terrarium.spatial.v1`

## What Iteration 3 established

Moss now inhabits an authored physical room rather than moving as a coordinate through illustration. Host-owned world/event authority defines walkable bounds, furniture blockers, deterministic room waypoints, approach anchors, supported sleep geometry, contact points, and the route used for each physical action. The renderer only interpolates the authoritative route.

Zone arrivals are now on usable floor: window at the sill-side floor/perch, shelf in front of the accessible collection tray, desk on its open side, and the sleeping nook at its entrance. Sleep always enters the supported bed anchor; wake holds a real wake pose then exits through the bed gate. Object inspect/pickup/place explicitly separate the semantic target, physical approach, and reachable contact point. Existing persisted object history is not silently rewritten; future placements use accessible authored slots.

The renderer follows deterministic route polylines with calm turns and route-segment facing. Carried props transition continuously across turns rather than flipping sides. Small room-art changes clarify physical affordances while preserving the accepted Iteration-2 style.

## Acceptance

- pytest: **26/26 PASS**;
- Python 3.10 grammar guard: **PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **PASS**;
- behavior evaluator seed 1701 / 500: **PASS**, **188 decisions + 312 continuations**, 10 action classes, all 6 objects moved;
- spatial evaluator seed 1701 / 500: **PASS**, **62 routed actions**, **41 multi-segment routes**, **23 carried routes**, **47 targeted interactions**, **0 blocker intersections**, **0 invalid awake endpoints**;
- exact replay at deterministic tick 698: **PASS**, canonical/replayed hash `5415606c3265ea5bb0166adfcaefba77fe132a324c64d9863dd3bd8347425fdd`;
- deterministic real-browser repeat: byte-identical SHA256 `607ee52244330be6734cee5e3e706ede57669de70dc8b67c0ee1b6c94a561ea9`;
- continuity interruption: **0 px**;
- real RAF: **16.5 ms min / 16.7 ms p50 / 16.8 ms p95 / 16.8 ms max**, zero >34 ms / >50 ms;
- promoted behavior auditor: sequence integrity true, 10 action classes, 47 object interactions;
- promoted grid-aware temporal auditor: **6/6 applicable tasks PASS**, zero critical failures and zero grid mismatches;
- human 800×480 inspection: **accepted**.

The promoted straight-vector temporal auditor is deliberately not used as an oracle for multi-turn routes. Those routes are covered by Terrarium's route-aware spatial evaluator plus real-browser telemetry and inspection.

## Pixel-art / pacing invariants

`ART_DIRECTION.md` remains visual authority. Internal art stays **400×240**, displayed as exact **2× nearest-neighbor 800×480** with smoothing off. The heartbeat remains **3 real seconds**, world advance **1 minute/heartbeat**, full day ~**72 real minutes**, and behavior commitments continue across heartbeats. The existing behavior RNG rules version remains `terrarium-rules-v2-action-pacing`; spatial geometry is versioned separately.

## SBC conclusion

Existing SBC/project-factory infrastructure and promoted behavior/temporal capabilities were sufficient. Spatial correctness is product-specific and is covered inside Terrarium. No capability was forged, no SBC files were modified, and **Gen18 is not warranted**.

## Runtime / Git safety

Canonical Moss state remains user-owned and outside Git. Only `data/.gitkeep` may be tracked from runtime storage. Deployment must preserve the existing canonical runtime directory, event chain, seed, object history, and SQLite database.
