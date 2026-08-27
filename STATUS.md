# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. This checkpoint is **not Generation 18**.

## Current checkpoint

Latest product checkpoint: **Action choreography, composition, and pacing** (`history/2026-08-27-action-choreography-pacing.md`).

Meaningful snapshot: `20260827T175337017716Z-action-choreography-pacing` — deterministic seed **1701**, tick **698**; dusk collection-shelf inspection of `amber_leaf`; frame SHA256 `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`; renderer SHA256 `17feafe5e5c0c6327df0bef5aa00f5617847949dbd0e23e41516a37240f8a61a`.

Primary evidence: `artifacts/action-choreography-pacing.json`. Deterministic Canvas fixtures remain in `artifacts/temporal-render-fixtures.json`.

Inherited guarantees remain intact: host-owned canonical state; deterministic seeded simulation; append-only/hash-chained event history; immutable snapshots + exact subsequent-event replay; disposable presentation-only renderer; fixed hardware-neutral 800×480 `TerrariumFrame`; persistent objects/habitat wear/aftermath; canonical living state outside Git.

## Pacing model — do not collapse these scales

The authoritative runtime heartbeat remains **3 real seconds**. It no longer means “choose a new action every three seconds.” Canonical deterministic action commitments allow Moss to hold one readable intention across multiple heartbeats:

- 6 seconds: idle, walk/explore, carry, place, wake;
- 9 seconds: rest, inspect;
- 12 seconds: window watching;
- 15 seconds: sleep.

These are semantic commitment windows, not animation durations. Renderer locomotion/contact interpolation stays faster (roughly 1.5–2.3 seconds for travel, with pose/contact/settle changes over fractions of seconds to a few seconds) and remains non-authoritative. Continuation frames preserve the current action clock rather than restarting it.

Seed 1701 / 500 heartbeats now produces **186 new decisions + 314 continuation/settle ticks**, approximately one new decision every **8.06 real seconds** on average while retaining all 10 action classes.

Environmental time is deliberately slower again:

- `tick_seconds`: **3.0**;
- `minutes_per_tick`: **1** (previously 8);
- full 24-hour day: **72 real minutes** (previously 9);
- dawn: ~**6 min** real;
- day: ~**28.5 min**;
- dusk: ~**6 min**;
- night: ~**31.5 min**;
- deterministic 180-world-minute weather block: ~**9 real minutes**.

The renderer gradually blends authoritative `world_minutes` through dawn/day/dusk/night transitions. Real-clock synchronization remains deferred; deterministic canonical time is still authoritative.

## Action choreography / composition

Interactions now use authoritative target metadata rather than renderer-invented targets. Moss adopts a bounded near-target stance, faces/gazes toward the target, and uses restrained head/ear/tail/body/paw changes to make actions distinct.

Accepted staging includes:

- inspect: approach/orient → target-relative lean/gaze → readable hold → recovery;
- pickup: approach/reach → contact → surface-to-Moss transfer → rigid paw/chest attachment;
- carry: stable attachment with a lower, steadier carrying posture;
- place: stop/prepare → lower → surface contact → release → settle → retract;
- window: sill-side planted observation with sparse fidgeting;
- sleep/wake: supported nook curl/unfold with facing consistent with travel.

Foreground shelf lips and the activity-desk front edge now provide intentional occlusion; the existing blanket lip continues to overlap supported sleep poses. No clutter, random camera motion, random zoom, or uncontrolled rendering entropy was added. `ART_DIRECTION.md` already contained the reusable contact/depth/motion rules needed, so it did not require revision.

## Behavior regression

Visual Maturity baseline → current seed-1701/500 decision behavior:

- action classes: **10 → 10**;
- decision entropy: **3.103385 → 3.165646 bits**;
- consecutive movement pairs: **19 → 6**;
- immediate zone reversals: **5 → 3**;
- max movement burst: **2 → 2**;
- adjacent manipulation pairs: **7 → 1**;
- max manipulation burst: **3 → 2**;
- moved objects: **6 → 6**.

Current decisions include 29 inspections, 12 pickups and 11 placements. The promoted `simulation-behavior-auditor-r1` (`932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`) passed the 186 decision-event stream with 10 action classes, entropy `3.165646`, max decision repeat run 4 sleeps, 52 object interactions, and sequence integrity.

## Objective temporal evidence

The promoted `temporal-render-auditor-r1` (`5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`) remains the objective temporal authority.

The first post-change run correctly rejected pickup/place endpoint settling (`0.104904`) and a sleep facing/settling defect. Acceptance was withheld. After stronger endpoint easing and authoritative sleep-facing correction, fresh real-Canvas evidence passed all representative tasks:

- left/right/arrival endpoint-speed ratios: `0.016821–0.020577`;
- carried walk: `0.026764`, attachment span **0**;
- pickup/place: `0.04986`;
- sleep: `0.095074`, facing mismatch **0**;
- continuity interruption jump: **0 px**;
- RAF: 157 intervals, max **16.8 ms**, **0** stalls over 50 ms.

Repeated deterministic `left_walk` capture is byte-identical at SHA256 `c25fa97c9870a5bc476f45f38ce2683b7fc9b0503e3675d3a9500688cb9a5a9f`.

These metrics are not a beauty score. Human inspection of the actual 800×480 Canvas governs interaction readability, silhouette/personality, composition, depth, calmness and environmental distraction.

## Regression

- pytest: **20/20 PASS**;
- JavaScript syntax: **PASS**;
- Python 3.10 syntax grammar: **PASS**, 22 files;
- technical evaluator: **PASS**;
- exact replay: **PASS**, canonical/replayed hash `2009ab06dc65bcf72379766a8a5345b0ee70bb6b2f7f9a8674ec08ad35036a5c`;
- behavior evaluator seed 1701 / 500: **PASS**;
- promoted behavior auditor: **PASS**;
- promoted temporal auditor: **PASS**;
- real RAF probe: **PASS**;
- deterministic repeat capture: **PASS**;
- real hero-scene visual inspection: **PASS**.

## SBC conclusion

Existing accepted SBC mechanisms were sufficient. No new capability was forged, no permanent MCP surface was added, and frozen Optiplex_MCP was not modified. **No Gen18 warranted.**

## Runtime / remote safety

Canonical Moss state lives outside Git in the user-owned runtime directory. Development evaluation used disposable temporary state and did not touch the canonical database. `origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use only the mediated project-safe Git push path and never copy credentials into the repository.

A development service or snapshot view is not a canonical LAN deployment. Report a deployment URL only after the actual host-owned runtime has been independently verified from the available safe boundary.

## Highest-value next product work

Let real human UAT drive the next normal Terrarium iteration. Prefer high-impact visible shortcomings in acting, composition, persistence and world believability over feature count. Keep moment/action/behavior/environment scales distinct, and only propose Gen18 when a concrete project need demonstrates a reusable SBC substrate deficiency.
