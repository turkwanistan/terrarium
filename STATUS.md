# Terrarium Status

Checkpoint: **POST-GEN17 PRODUCT CHECKPOINT — TEMPORAL AFTERMATH POLISH**.

This is normal Terrarium development after the accepted Generation 17 pilot. It is **not Generation 18**.

## Current product state

The room already records what Moss has been doing through persistent `habitat.activity_aftermath`; the latest checkpoint improves how that history becomes visible. Existing window traces, activity-corner clutter, and sleeping-nook wear now emerge progressively instead of appearing in discrete renderer count buckets. The renderer also gives those persistent traces restrained weather/ambient response while remaining disposable and non-authoritative.

Meaningful snapshot: `20260827T115103702156Z-temporal-aftermath-polish` (seed 1701, tick 240). Evidence: `artifacts/temporal-aftermath-polish.json` and `history/2026-08-27-temporal-aftermath-polish.md`.

Inherited Gen17 guarantees remain intact:

- fixed hardware-neutral logical renderer: **800×480**;
- persistent canonical creature/world state outside the renderer;
- deterministic seeded simulation and exact snapshot + subsequent-event replay;
- append-only/hash-chained event history;
- process/browser restart persistence;
- autonomous idle/walk/explore/rest/sleep/wake/look-outside/inspect/carry/place behavior;
- multiple habitat zones, persistent objects, persistent habitat wear, and persistent activity aftermath;
- canonical living state is user-owned outside Git; renderer is disposable/non-authoritative.

Latest visible improvement:

- activity-aftermath changes interpolate over **1.8 seconds** between authoritative frame updates;
- **26 authored layers** now emerge progressively: 5 window smudges, 5 wet-window streaks, 4 bedding creases, 5 activity-corner papers, and 7 work marks;
- stable hash-derived micro-variation gives traces/papers organic placement without `Math.random` or renderer-owned state;
- rain/mist/clear conditions alter how already-persistent window history reads;
- bedding compression, pillow shift, and creases grow continuously from actual sleep history;
- generic path-wear routes are slightly quieter so activity-specific aftermath has clearer visual priority.

Meaningful development snapshot:

- `20260827T115103702156Z-temporal-aftermath-polish`
- deterministic seed **1701**, tick **240**
- frame SHA256 `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`
- renderer SHA256 `9e727e04145c5a084555970d0a8bb7c269a6ba27c6b51db46e0324103f55fbd3`

The frame SHA is intentionally identical to the previous activity-aftermath checkpoint; this iteration changes presentation, not canonical world outcome.

## Evidence

Current checkpoint regression:

- pytest: **14/14 PASS**;
- JavaScript syntax check: **PASS**;
- Python 3.10 syntax compatibility: **PASS**;
- technical evaluator: **PASS** — exact replay, event-chain integrity, append-only SQLite enforcement, restart equality, fixed 800×480 frame;
- behavior evaluator seed 1701 / 500 steps: **PASS** — accepted action distribution unchanged, entropy **3.151553 bits**, 28 placements, 28 pickups, 58 inspections, all 6 objects moved, 10 persistent habitat marks.

Temporal-aftermath evidence (`artifacts/temporal-aftermath-polish.json`):

- previous renderer SHA256 `9083851633567c9e520020b252b61c23ecd5f85ca68609da9b780af848ebac0c` → current `9e727e04145c5a084555970d0a8bb7c269a6ba27c6b51db46e0324103f55fbd3`;
- previous and current seed-1701/tick-240 semantic frame SHA256 are both `12624190b1759215a62d4ffa3af70aa5ac759940f32b7c8362301e0fb043334e`;
- same-horizon semantic frame equality: **true**;
- seven old activity-specific discrete stage-rule tokens detected before, **zero** remaining after;
- renderer `Math.random`: **absent**;
- stable deterministic micro-variation and weather-conditioned persistent-window rendering: **present**.

Earlier spatial/activity evidence remains valid in `artifacts/visual-storytelling-comparison.json`, `artifacts/visual-storytelling-counterfactual.json`, and `artifacts/activity-aftermath-comparison.json`.

## Browser inspection

The actual Canvas renderer was inspected at 800×480 through the mediated browser:

- accepted tick-240 aftermath scene before the change;
- updated tick-240 scene with the exact same semantic frame;
- deterministic tick-720 accelerated scene with all three aftermath classes present: 14 sleeping-nook sleep ticks across 4 bouts, 30 window watches, and 67 activity-corner uses;
- temporary rain + wet-window renderer counterfactual, viewed twice 1.2 seconds apart to exercise the ambient weather-bound trace animation;
- final milestone snapshot opened through the real Canvas renderer.

Temporary inspection frames were removed before snapshot capture. Automated evidence does **not** claim to measure subjective warmth, charm, or beauty; perceptual judgment came from renderer inspection.

## Self-Building Computer / capability evidence

No new reusable capability gap was needed for this checkpoint.

Existing promoted capability:

- `simulation-behavior-auditor-r1`
- content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`
- evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae`

Post-change regression reuse: **PASS** via Forge run `cap_20260827T115050Z_933e3d93`. The current deterministic 180-event audit input SHA256 `fa438bef63e3aa56b353638b27b42248c06682347d4b8684cca3fc2874df5b11` matched the held-out vector exactly; result: 10 action classes, entropy **3.174454**, 42 object interactions, `sequence_ok=true`.

Candidate procedural memories remain non-authoritative. No applicability, evaluation, or promotion gate was weakened. Operational Lab remains `gen6-experience-memory-r1-dc0d2cb41595`; permanent MCP surface remains 10. Frozen Optiplex_MCP was not modified.

## Inherited Gen17 runtime proof

- browser close/reopen advanced authoritative tick/event **36 → 63** while the renderer was closed;
- process restart resumed persisted state and reached tick/event **87** rather than resetting;
- stopped final live proof reached **402 events/ticks** with exact replay hash `b3d10eda99f8b3ba580043d4d7c40bd1ce0cde0f9cbc45cde019fb3d1fc21a1b`;
- compact event redesign reduced the observed 100-event JSONL footprint from ~889 KB to ~124 KB while preserving replay.

## Highest-value next product improvement

Make **present activity and accumulated aftermath feel causally connected in the renderer**. When Moss is currently sleeping, watching the window, or using the activity corner, let the already-existing traces respond subtly to that action/environment. Keep it renderer-only unless evidence reveals a real world-model gap; do not add dashboards, dialogue, learned routines, hardware work, or broad mechanics yet.

## Development / runtime policy

- milestone snapshots: `snapshots/dev/`; standard comparison scene seed 1701 / step 240;
- local gallery: `/snapshots/`; renderer/source hashes pin historical identity;
- canonical trusted-LAN launch: `scripts/run_lan.sh`;
- runtime state defaults to `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` and must remain outside Git;
- repo-local `data/*` is ignored except `.gitkeep` and is development/legacy-only;
- normal development creates one tested commit/push attempt per meaningful checkpoint.

## Canonical runtime deployment status

The repository source is updated, but the actual host-owned Moss runtime could not be safely inspected or restarted from the available mediated boundary: the canonical user-owned runtime directory is outside the project workspace, while the browser development service is isolated and non-canonical. No replacement world was created and canonical runtime state was not touched. A LAN URL is therefore not claimed until the real host runtime can be verified.

## Remote

- `origin`: `git@github.com:turkwanistan/terrarium.git`
- `main` tracks `origin/main`
- mediated push uses project-scoped credentials and must not be bypassed by copying secrets into the repo.
