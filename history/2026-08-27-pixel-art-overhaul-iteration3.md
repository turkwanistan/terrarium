# Pixel-Art Overhaul — Iteration 3: Spatial Coherence and Physical Acting

Accepted after Iteration 2 exposed spatial illusion breaks: semantic zone anchors inside illustrated furniture, straight-line traversal through blockers, unsupported sleep, and interaction stance derived from simplistic coordinate offsets.

## Change

Terrarium now owns a minimal authoritative single-room spatial model (`terrarium.spatial.v1`). It defines usable floor, major furniture blockers, a small deterministic waypoint graph, zone/interaction approach geometry, contact points, and a supported bed location. Route choice is deterministic and recorded in event/frame data. The renderer follows that route; it does not choose where Moss may stand.

Window, shelf, and activity-corner anchors now live on believable usable sides. Inspect/pickup/place distinguish semantic target, physical approach, and reachable contact. Sleep always routes into the supported bed anchor. Wake is an explicit pose and its continuation exits through the bed gate before ordinary decisions resume. Existing canonical object history is preserved; future placements use accessible authored slots.

The Canvas renderer now follows multi-segment authoritative routes at deterministic arc length, turns at route boundaries, and preserves the Iteration-2 sprite vocabulary. Carried props remain continuous through facing changes. Small pixel-native perch/tray/lip details clarify spatial affordances and depth without changing the accepted art direction.

## Evidence

- pytest 26/26 PASS; Python 3.10 grammar and JS syntax PASS;
- technical and behavior evaluators PASS;
- spatial evaluator PASS: 62 routed actions, 41 multi-segment routes, 23 carried routes, 47 targeted interactions, 0 blocker intersections, 0 invalid awake endpoints;
- exact deterministic 698-tick replay PASS, hash `5415606c3265ea5bb0166adfcaefba77fe132a324c64d9863dd3bd8347425fdd`;
- deterministic browser repeat byte-identical SHA256 `607ee52244330be6734cee5e3e706ede57669de70dc8b67c0ee1b6c94a561ea9`;
- continuity interruption 0 px; real RAF max 16.8 ms with no >34/50 ms stalls;
- promoted behavior auditor preserved sequence integrity/diversity;
- promoted grid temporal auditor passed 6/6 applicable straight/single-segment tasks with zero critical/grid failures;
- real 800×480 inspection accepted window, bed, wake exit, shelf, activity-corner, object, and carried-route staging.

Multi-turn routes are intentionally judged by route-aware Terrarium spatial evaluation plus real temporal telemetry, because the promoted grid auditor's facing/reversal model assumes a single straight semantic vector.

## SBC conclusion

No reusable substrate deficiency was demonstrated. Spatial evaluation is Terrarium-specific; existing promoted behavior/temporal capabilities were sufficient. No capability was forged and Gen18 is not warranted.

## Snapshot

`20260827T204232352544Z-pixel-art-overhaul-iteration3` — seed/tick 1701/698; frame SHA256 `fe7ffd8dbefc56144c7af673a810339f136ae6f08db580cf80bc8b819f0996a9`; renderer JS SHA256 `96bd0eb952cf40b8b5099b1b7ab47ca376bc46339c01ebd0556ed440f1f8115d`; 400×240 art surface displayed exact 2× at 800×480.
