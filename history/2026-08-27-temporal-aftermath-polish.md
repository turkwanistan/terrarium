# Post-Gen17 product checkpoint — Temporal aftermath polish

Date: 2026-08-27

This is normal Terrarium product development, **not Generation 18**.

## Product change

This checkpoint keeps the existing canonical world and activity-aftermath counters unchanged while improving how their accumulated physical consequences emerge in the 800×480 renderer.

- Activity-aftermath counter changes interpolate over 1.8 seconds instead of visually snapping between polled frames.
- Five window smudges, five weather streaks, four bedding creases, five activity-corner papers, and seven work marks now emerge as independently faded authored layers rather than integer-count buckets.
- Stable hash-derived micro-variation gives papers and traces less mechanical placement without `Math.random` or renderer-owned persistent state.
- Existing wet-window history responds to current conditions: rain adds restrained glints/beads, mist softens persistent smudges, and clear weather leaves dried traces quieter.
- Bedding compression, pillow drift, and crease strength grow continuously from actual sleep history, with only sub-pixel ambient cloth motion.
- Generic worn travel routes were slightly reduced in opacity/width so activity-specific physical history has clearer visual priority.

No simulation rules, action weights, canonical state schema, `TerrariumFrame` contract, RNG, or replay behavior changed.

## Deterministic evidence

`artifacts/temporal-aftermath-polish.json` isolates the renderer change from world evolution:

- accepted activity-aftermath renderer SHA256: `9083851633567c9e520020b252b61c23ecd5f85ca68609da9b780af848ebac0c`;
- new renderer SHA256: `9e727e04145c5a084555970d0a8bb7c269a6ba27c6b51db46e0324103f55fbd3`;
- accepted and current seed-1701/tick-240 semantic frame SHA256 are both `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`;
- same-horizon semantic frame equality is `true`;
- seven prior activity-specific discrete stage-rule tokens are present in the old renderer and zero remain in the new renderer;
- the renderer has 26 progressively emerging authored aftermath layers and still contains no `Math.random`.

This evidence is intentionally objective. It does not claim to measure warmth, charm, or subjective visual quality.

## Canvas inspection

The real Canvas renderer was inspected at 800×480 through the mediated browser:

- the accepted tick-240 aftermath scene before the change;
- the updated tick-240 scene with the same semantic frame;
- an accelerated deterministic tick-720 scene with all three aftermath classes present: 14 sleeping-nook ticks across 4 bouts, 30 window watches, and 67 activity-corner uses;
- a temporary renderer-only rain counterfactual with wet-window history, inspected twice 1.2 seconds apart to verify the weather-bound ambient trace animation actually runs.

The temporary inspection frames were removed before the milestone snapshot; they are not part of the snapshot trail.

## Regression / SBC evidence

Final regression:

- pytest: **14/14 PASS**;
- JavaScript syntax check: **PASS**;
- Python 3.10 compatibility: **PASS** through the existing test suite;
- technical evaluator: **PASS**, including exact replay, event-chain integrity, append-only SQLite enforcement, restart equality, and fixed 800×480 frame;
- behavior evaluator seed 1701 / 500 steps: **PASS** with the accepted action distribution unchanged and entropy **3.151553 bits**.

The promoted `simulation-behavior-auditor-r1` capability was reused on the matching 180-event deterministic stream. Input SHA256 `fa438bef63e3aa56b353638b27b42248c06682347d4b8684cca3fc2874df5b11` matched the current post-change stream and the held-out audit vector. Run `cap_20260827T115050Z_933e3d93` passed with 10 action classes, entropy `3.174454`, 42 object interactions, and `sequence_ok=true`.

No new reusable Self-Building Computer capability gap was justified. The existing candidate procedural memories remain non-authoritative and no evidence/promotion gate was weakened.

## Snapshot

`20260827T115103702156Z-temporal-aftermath-polish` — seed 1701, tick 240, frame SHA256 `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`, renderer SHA256 `9e727e04145c5a084555970d0a8bb7c269a6ba27c6b51db46e0324103f55fbd3`.

The unchanged frame hash is intentional: this checkpoint improves how the same authoritative accumulated history is rendered.

## Highest-value next product work

Make **present activity and accumulated aftermath feel causally connected in the renderer**: while Moss sleeps, watches the window, or uses the activity corner, let the already-existing physical traces react subtly to the current action and environment. Keep it renderer-only unless evidence exposes a real world-model gap; do not add dashboards, conversation, routines, or broad mechanics yet.
## Canonical runtime deployment boundary

The canonical host-owned runtime was **not substituted with an isolated development service**. The available mediated project tooling exposes the repository but rejects the user-owned canonical runtime directory as outside the workspace, and the Lab connector is a separate disposable VM. Therefore this session could update the canonical Terrarium source repository but could not safely inspect/restart the actual Moss process or verify its LAN endpoint. No replacement world was initialized and no canonical SQLite/WAL/SHM/event-ledger state was touched.

