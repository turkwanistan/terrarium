# 2026-08-27 — Action choreography, composition, and pacing

Accepted normal Terrarium product checkpoint after Visual Maturity. This is **not Generation 18**.

## Outcome

Moss now behaves on deliberately separated time scales instead of treating every three-second world heartbeat as a new visible intention. Canonical action commitments preserve deterministic autonomy while allowing inspect, carry, place, window-watch, rest, sleep, and recovery states to remain readable. The renderer remains presentation-only.

Interactions are target-aware: authoritative event/frame metadata supplies the object or destination, Moss adopts a bounded near-target stance, faces and looks toward it, reaches/contact stages around it, carries the prop at a rigid paw/chest offset, and places it through stop → lower/contact → release → settle → retract. Shelf lips, desk front edge, and the existing bed/blanket overlap provide intentional foreground occlusion.

The world clock now advances **1 world minute per 3 real seconds** instead of 8. A full day therefore lasts **72 real minutes** instead of 9. Dawn lasts about 6 minutes, day 28.5, dusk 6, and night 31.5; deterministic weather blocks last about 9 minutes. The renderer interpolates authoritative world time through gradual lighting changes rather than abruptly swapping phase palettes. Real-clock synchronization remains deferred to preserve deterministic authority.

## Behavioral pacing evidence

Seed 1701 / 500 heartbeats:

- new decisions: **186**; continuation/settle heartbeats: **314**;
- all **10** action classes retained;
- decision entropy: **3.165646 bits**;
- movement pairs: **19 → 6**;
- immediate reversals: **5 → 3**;
- manipulation adjacency: **7 → 1**;
- max movement burst: **2**; max manipulation burst: **2**;
- all **6** objects still moved.

The promoted `simulation-behavior-auditor-r1` (`932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`) independently passed the 186 decision-event stream: diversity 10, entropy 3.165646, max decision repeat run 4 sleeps, 52 object interactions, sequence integrity PASS.

## Temporal evidence and iteration

The first post-change promoted temporal audit correctly found three residual choreography defects: short pickup and placement endpoint-speed ratios were `0.104904` against a `0.10` limit, and sleep movement faced the wrong direction while settling too sharply. The iteration was **not accepted** at that point.

After stronger endpoint easing and authoritative sleep-facing correction, fresh real-Canvas evidence passed `temporal-render-auditor-r1` (`5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`) on all representative tasks. Pickup/place settle ratio is `0.04986`, sleep is `0.095074` with zero facing mismatches, carried attachment span is 0, continuity interruption jump is 0 px, and real RAF max is 16.8 ms with zero >50 ms stalls.

Repeated deterministic `left_walk` capture was byte-identical at SHA256 `c25fa97c9870a5bc476f45f38ce2683b7fc9b0503e3675d3a9500688cb9a5a9f`.

## Visual review

Real 800×480 Canvas inspection covered inspect, pickup, placement, sleep, wake, window, activity corner, populated room, dawn, dusk, and the accepted snapshot. Target/contact readability, Moss silhouette/personality, prop ownership, quiet idle/window behavior, furniture depth, and gradual environment lighting were accepted. No beauty score was introduced; automated checks remain correctness tools, while `ART_DIRECTION.md` plus real visual review govern aesthetics.

## Regression

- pytest: **20/20 PASS**;
- JavaScript syntax: **PASS**;
- Python 3.10 grammar compatibility: **PASS**, 22 Python files;
- technical evaluator: **PASS**;
- exact replay: **PASS**, canonical/replayed hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator seed 1701 / 500: **PASS**;
- promoted behavior auditor: **PASS**;
- promoted temporal auditor: **PASS**;
- real RAF probe: **PASS**;
- deterministic repeated capture: **PASS**.

Primary evidence: `artifacts/action-choreography-pacing.json`.

## Snapshot

`20260827T175337017716Z-action-choreography-pacing` — seed **1701**, tick **698**, dusk, collection-shelf inspection of `amber_leaf`; frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`; renderer SHA256 `17feafe5e5c0c6327df0bef5aa00f5617847949dbd0e23e41516a37240f8a61a`.

The frame was opened and inspected through the actual fixed 800×480 Canvas renderer. At this tick all six objects have moved and seven persistent marks exist, so the snapshot demonstrates target interaction, accumulated history, depth and the slower dusk cadence together.

## SBC conclusion

Existing promoted behavior/temporal auditors, isolated Optiplex_Lab, mediated browser, compact evidence transport, and project-safe lifecycle were sufficient. No capability was forged and no permanent MCP surface changed.

**No Gen18 warranted.**
