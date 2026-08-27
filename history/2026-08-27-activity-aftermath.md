# Post-Gen17 product checkpoint — Activity aftermath

Date: 2026-08-27

This is normal Terrarium product development, **not Generation 18**.

## Product change

Existing activities now leave deterministic physical aftermath derived from canonical history rather than generic decoration:

- repeated window-watching accumulates pane smudges and sill wear; current rain/mist still changes the environmental rendering around those persistent traces;
- activity-corner use progressively rearranges papers and adds small work marks;
- sleep in the sleeping nook accumulates a compressed nest, pillow displacement, and bedding creases once actual sleep history exists.

The persistent derived state is `habitat.activity_aftermath`. Existing canonical worlds remain compatible: missing counters initialize lazily on the next simulation step. The action-selection RNG and `RULES_VERSION` are unchanged.

## Comparison evidence

`artifacts/activity-aftermath-comparison.json` compares fresh seed 1701, the previous accepted `lived-in-staging` checkpoint at tick 240, the improved implementation at the same seed/tick, and accelerated life at tick 720.

- fresh tick 0: 0 recognizable activity-specific cues;
- previous checkpoint tick 240: 0 activity-specific aftermath counters;
- improved same-horizon tick 240: 11 window watches and 17 activity-corner uses, giving 2 recognizable activity classes;
- improved tick 720: 30 window watches, 67 activity-corner uses, and 14 sleeping-nook ticks across 4 bouts, giving all 3 activity classes.

After removing only the new `activity_aftermath` frame field, the previous checkpoint and improved same-horizon frame are exactly equal. This proves the existing action/object/path-wear outcome is unchanged and the visual difference comes from the new accumulated-history presentation.

## Regression / SBC evidence

- pytest: 14/14 PASS;
- Python 3.10 syntax compatibility: PASS;
- technical evaluator: PASS, including exact replay, hash-chain integrity, append-only enforcement, restart equality, and 800×480 frame contract;
- behavior evaluator seed 1701 / 500 steps: PASS with the exact accepted action distribution and entropy 3.151553 bits;
- promoted `simulation-behavior-auditor-r1` reused on a fresh 180-event stream: PASS, 10 action classes, entropy 3.174454, 42 object interactions, sequence intact; run `cap_20260827T054348Z_b67454cd`.

No new reusable Self-Building Computer capability gap was justified. Candidate procedural memory remained non-authoritative and was not promoted.

## Snapshot

`20260827T054359565518Z-activity-aftermath` — seed 1701, tick 240, frame SHA256 `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`.

The accelerated tick-720 world was also inspected through the real Canvas renderer.
