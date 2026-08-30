# Terrarium — Godot Web Deep Debug Iteration

## Status and purpose

The Godot Web canary has reached its first real human UAT and **failed presentation acceptance**.

Observed in the ordinary browser build against the real persistent Terrarium world:

- Moss visibly teleports between positions instead of moving continuously;
- most authored Moss action animation is absent, too brief, or appears frozen/static;
- the Web build therefore does not yet provide behavioral/presentation parity with the previously validated native Godot candidate.

This is a **presentation/runtime integration defect**, not evidence that the canonical simulation should change. The existing Canvas renderer remains the accepted same-world fallback. Godot Web migration is not closed, and Iteration 10 must not begin until this debug iteration either passes the Web cutover gate or the Web migration is deliberately deferred.

## Non-negotiable authority and safety constraints

1. The canonical world/API/database/event history remain host-owned and authoritative.
2. Godot remains a read-only presentation client of canonical `terrarium.frame.v1`.
3. Do not change simulation pacing, commitments, routes, actions, target selection, object authority, database state, or world history to hide a renderer defect.
4. Do not reset, recreate, migrate, force-step, or replace the live world for debugging.
5. Canvas at the existing canonical API remains the immediate rollback/reference presentation.
6. Production Moss remains exact authored `display/art/moss/*.json` geometry translated through `MOSS_MAP`; do not redesign Moss during this iteration.
7. Preserve the accepted room composition/art direction unless evidence proves a Web-specific rendering defect requires a presentation-only fix.
8. Native Godot validation in `mcp-lab` must follow `GODOT_NATIVE_VALIDATION.md`: one bounded process/capture at a time, hard timeout, cleanup/process/load checks, no large llvmpipe batches.
9. Do not run an always-on native Godot renderer through Lab/Xvfb/llvmpipe.
10. Do not begin Iteration 10 during this debug iteration.

## Current relevant architecture

- canonical world/API: `terrarium.api.server`, normally live on host port `8765`;
- Canvas fallback: `display/web/`;
- Godot source: `display/godot_reference_v2/`;
- live adapter: `display/godot_reference_v2/scripts/frame_adapter.gd`;
- presentation runtime: `display/godot_reference_v2/scripts/main.gd`;
- Web export: `display/web/godot/`, generated from source commit `d6a308af9f73bd1404efd179a929af45b2d285c8` by Godot 4.7.2;
- generated build commit: `8c591089c7181621e125fc824c4a04509718ad86`;
- Web export is single-threaded and derives its live API origin from the serving page;
- HTTPS read-only gateway: `tools/godot_web_gateway.py` + `scripts/run_godot_web_canary.sh`;
- gateway exposes only `GET /api/frame` and `GET /api/health`; world writes remain blocked.

The live adapter currently polls `GET /api/frame` every 3 seconds. `main.gd` maintains a separate motion clock and a route-transition clock. Route interpolation currently uses the previous canonical frame/route as its starting evidence rather than explicitly rebasing each new transition from Moss's **currently rendered** position. This is a high-priority continuity hypothesis, but it must be proven rather than assumed.

## Definition of done

The iteration is complete only when an ordinary browser running the exported Godot Web build against the real persistent world demonstrates all of the following:

- no visible teleport on canonical frame arrival or route/action transition;
- every canonical position change is rendered as continuous, spatially coherent movement unless the canonical semantic contract itself explicitly represents an instantaneous change;
- walk/explore animation remains visibly alive throughout locomotion;
- nudge, inspect, groom, stretch, carry/pickup choreography, place, react/look, window-watch, sleep, wake, rest, loaf, and idle use their intended authored presentation rather than collapsing to generic/static poses;
- continuation heartbeats do not replay anticipation from frame zero;
- sustained actions also do not simply freeze forever on a terminal keyframe: they use an intentional hold/loop/resting phase appropriate to the authored action;
- facing remains coherent through routes and turns;
- carried objects stay attached through movement/turns and place cleanly releases/settles them;
- sleep/wake support and bed occlusion remain coherent;
- lighting/weather/season selection follows canonical frame state;
- Web and native Godot given the same deterministic frame sequence produce equivalent semantic motion/action choices, allowing only platform-specific frame timing/rendering differences;
- browser console contains no recurring HTTP, WebAssembly, resource, timing, or Godot script errors during the accepted run;
- gateway remains read-only and the canonical world continues uninterrupted;
- no renderer process/service causes abnormal CPU growth or process leakage;
- Canvas fallback remains intact;
- full repository tests and new Web-specific regression tests pass;
- 30–60 minutes of real-world Web UAT, or an equivalent evidence-backed natural-transition session plus targeted deterministic rare-action checks, passes before migration closure.

## Phase 0 — Freeze the failed canary and record evidence

Before changing implementation:

1. Update current project status/evidence to record that first real Godot Web UAT failed because of teleporting and missing/static animation.
2. Capture exact current Git state and generated Web build metadata.
3. Confirm Canvas still renders the same living world correctly.
4. Confirm the canonical API is healthy and advancing naturally.
5. Confirm no debug action resets or force-steps the world.
6. Preserve the failing Web build as a reproducible baseline; do not overwrite the evidence before measurements exist.

Deliverable: a small `artifacts/godot-art-gate/web-deep-debug/` baseline record containing source/build commits, live tick sample, browser/runtime details available from tooling, and the observed failure statement.

## Phase 1 — Instrument the presentation pipeline before fixing it

Add bounded **presentation-only diagnostic telemetry** sufficient to answer what happens from canonical frame arrival to final rendered pixels. Do not add a second world model.

Capture at minimum:

- canonical frame tick and arrival timestamp;
- interval since previous accepted frame;
- creature activity, pose, zone, x/y, facing, carrying, target object;
- last-event action and route points when present;
- selected Godot motion;
- whether the motion changed or continued;
- `live_motion_started_ms` and motion elapsed time;
- transition start time and transition elapsed time;
- route points after visual mapping;
- actor's rendered position immediately **before** accepting a new frame;
- route interpolation start position;
- target visual position;
- actor rendered position after the frame is accepted and over the next transition;
- animation frame index over time;
- object attachment/release state;
- frame-adapter request start/completion/error and response tick.

For Web, expose diagnostics in a bounded way that can be collected from browser console or a small read-only debug surface/query mode. Diagnostics must be optional or low-noise in normal presentation and must never write canonical state.

Key question: determine whether the teleport is caused by canonical state, frame polling/cadence, route construction, transition rebasing, Web clock behavior, browser throttling, integer snapping, or another platform-specific discrepancy.

## Phase 2 — Build a deterministic Web reproduction harness

Do not rely on waiting for the living world to randomly reproduce every action.

Create deterministic fixture sequences of valid `terrarium.frame.v1` frames that cover:

1. idle → walk → continuation → arrival;
2. multi-segment route with a corner and facing change;
3. a new frame arriving before the prior visual transition is finished;
4. same-motion continuation heartbeats;
5. inspect contact/hold/recover;
6. nudge anticipation/contact/hold/recover;
7. groom and stretch sustained acting;
8. pickup→carry, carry movement/turn, place lower/contact/release/recover;
9. rest and loaf;
10. react/look and window-watch;
11. sleep entry/curl hold and wake/exit;
12. rain/night/environment changes;
13. duplicate tick and delayed response cases;
14. a response interval longer and shorter than the nominal three-second heartbeat.

Run the **actual exported Web build** against this fixture endpoint in a real browser. Collect deterministic telemetry and screenshots/frames where useful. The fixture server must be read-only and isolated from the live world.

Add automated regression assertions for continuity and motion-state semantics. Prefer testing measurable presentation state/telemetry over brittle pixel-perfect browser timing.

## Phase 3 — Establish native-vs-Web parity with identical inputs

The native candidate already passed bounded representative gates, but this iteration must isolate whether the regression is Web-specific or latent shared runtime logic.

Using the same deterministic frame fixtures:

- run the shared GDScript/state mapping logic in tests where possible;
- exercise the exported Web build in the browser;
- use only a **small representative** set of bounded native Godot 4.7.2 checks in Lab if platform parity cannot be established from source/state tests alone;
- never run a large native capture matrix.

For each fixture, compare:

- selected motion;
- motion-change vs continuation decision;
- animation phase/frame progression;
- mapped route points;
- interpolation start/target;
- facing;
- action-object identity/state/attachment;
- environment variant.

Classify every discrepancy as:

- canonical/frame-contract issue;
- shared Godot presentation bug;
- Web-only runtime/timing bug;
- browser delivery/gateway problem;
- expected platform rendering difference.

Do not modify simulation unless independent evidence proves the canonical frame contract is wrong.

## Phase 4 — Fix spatial continuity first

Teleporting is a release-blocking defect and should be solved before animation polish.

Investigate and, if confirmed, correct these likely failure classes:

### A. Rebase from the currently rendered position

When a new canonical frame arrives while the previous transition is still in progress, the next route should begin from Moss's **actual currently rendered presentation position**, not blindly from the prior canonical endpoint. This matches the already-established Terrarium renderer continuity lesson.

The fix must:

- snapshot current rendered actor anchor before replacing transition state;
- construct the next route from that visual anchor into canonical route/target evidence;
- preserve canonical target/route authority;
- avoid cumulative drift by ending exactly at the canonical mapped target;
- respect pixel-grid snapping without creating a large instantaneous jump.

### B. Handle routes absent on continuation frames

Prove how canonical walk/explore continuation frames encode position and `last_event.route`. If route evidence is absent while canonical position advances, interpolate from rendered current position to authoritative target instead of snapping.

### C. Separate frame-arrival cadence from transition duration

Measure actual Web request/response cadence. Do not assume an exact three seconds. Transition duration must remain visually coherent under modest jitter, late frames, and early frames. Avoid a design where a small timing mismatch produces a dead gap or jump.

### D. Duplicate/delayed/out-of-order protection

Duplicate ticks are already ignored. Add explicit handling/evidence for delayed/out-of-order frame responses if Web `HTTPRequest` behavior can produce them. Never move presentation backward to an older canonical tick.

### E. Arrival settle and facing

Ensure the final interpolated position equals the authoritative mapped target and that facing derives from movement direction while moving, then settles to canonical facing without a contradictory one-frame flip.

Acceptance for this phase: deterministic route fixtures show no instantaneous displacement at frame ingest beyond the permitted integer-grid quantization step; all movement ends at the exact mapped canonical target.

## Phase 5 — Repair animation lifetime and action-phase semantics

After spatial continuity is correct, audit every canonical activity against its intended authored sequence.

Current non-looping motion logic clamps many actions to the final frame. Combined with multi-tick canonical commitments, this can make actions appear unanimated or permanently frozen even though heartbeat replay was correctly removed. The solution must preserve the rule **"continuation heartbeat is not a new animation start"** while giving sustained actions an intentional presentation lifetime.

For each motion define an explicit presentation phase policy, for example:

- anticipation/start once;
- contact/engagement once;
- bounded sustained hold or small authored loop where appropriate;
- release/recovery once when semantic state changes;
- calm terminal pose only when that is genuinely the intended look.

Audit separately:

- idle: subtle authored life, not mechanical jitter;
- walk/explore: continuous loop while locomoting;
- inspect: readable approach/contact/hold without freezing unnaturally;
- nudge: anticipate/contact/press/hold/recover;
- groom: start/contact plus a calm bounded groom hold/loop;
- stretch: ready/extend/hold/recover;
- carry: pickup sequence only when transfer begins, then stable carry locomotion without replay;
- place: lower/contact/release/recover exactly once at semantic place;
- rest/loaf: intentionally distinct quiet acting;
- react/look: bounded look/orient acting;
- window-watch: sustained but alive observation;
- sleep: entry → supported curl → stable sleeping life;
- wake: wake sequence → exit exactly once.

Do not invent new canonical actions or timing authority. Presentation phases are renderer-owned and subordinate to canonical activity/state.

Acceptance for this phase: fixture telemetry proves animation frame progression for every mapped canonical activity, no continuation replay from frame zero, and no unintended terminal-frame freeze for sustained actions.

## Phase 6 — Object and support choreography regression

With movement and animation clocks corrected, re-run interaction-specific checks:

- target contact aligns with authoritative target object/zone;
- carried object attaches rigidly to Moss through locomotion and flips/turns;
- pickup choreography occurs once per transfer rather than every carry heartbeat;
- place moves through lower/contact/release and leaves the object at canonical state/position;
- sleep/wake remains supported by the bed geometry and occlusion layer;
- unknown object/zone state fails safely instead of producing fake authority.

Add regression fixtures for these cases in Web.

## Phase 7 — Web runtime/delivery hardening

Audit browser-specific mechanics independently of scene logic:

- verify Godot 4.7.2 Web console is free of recurring script/resource/WASM errors;
- verify `HTTPRequest` cadence and no overlapping-request failure loop;
- verify same-origin HTTPS `/api/frame` and `/api/health` behavior;
- verify tab-focus/background throttling behavior and define whether background-tab throttling is supported or simply excluded from UAT;
- verify `performance`/Godot tick clocks remain monotonic and suitable for presentation timing;
- verify Web export remains single-threaded unless evidence requires changing that decision;
- verify MIME types and cache policy do not serve stale `.pck`/`.wasm`/JS after a new build;
- improve `run_godot_web_canary.sh` port preflight so an occupied port fails with a clear diagnostic or safe alternate rather than a Python traceback;
- retain read-only gateway restrictions and fail-closed entry-page behavior.

Do not broaden the gateway into a second application server.

## Phase 8 — Automated gates

Add/extend tests so the discovered defects cannot regress silently.

At minimum:

1. pure mapping tests for every canonical activity → motion;
2. motion continuation tests proving same activity does not reset start time;
3. sustained-action phase progression tests;
4. current-rendered-position rebase test;
5. early-new-frame continuity test;
6. route-corner/facing test;
7. no-route continuation interpolation test;
8. delayed/duplicate/older-tick behavior test;
9. carry attachment + place release test;
10. sleep/wake support-state test;
11. actual exported-Web browser fixture test;
12. gateway read-only/security contract regression;
13. generated Web build source SHA/build-info verification.

Keep the full repository suite green throughout. If a test requires changing canonical behavior merely to make Godot pass, stop and reassess authority boundaries.

## Phase 9 — Real browser UAT against the living world

Only after deterministic Web fixtures pass:

1. rebuild the Web export from the accepted source revision;
2. deploy/pull the generated Web build to the OptiPlex;
3. start the HTTPS presentation gateway on a known-free port;
4. verify Canvas fallback first;
5. run the ordinary browser Godot presentation against the actual persistent world;
6. observe 30–60 minutes or enough natural transitions to cover multiple movements/actions/environment changes;
7. compare suspicious moments with Canvas against the same canonical world;
8. do not force the living world into rare actions just for coverage—use deterministic fixtures for those.

Human UAT questions:

- Does Moss ever visibly pop/teleport when a new heartbeat arrives?
- Does locomotion feel continuous through corners and arrivals?
- Can the viewer visibly distinguish Moss's major activities without reading debug text?
- Do sustained actions feel alive rather than frozen?
- Do carry/place and sleep/wake remain physically coherent?
- Does the scene remain calm, pixel-native, and faithful to the approved art direction?

Record failures with tick/time/activity plus screenshot/video when available so they can be correlated to diagnostic telemetry.

## Phase 10 — Acceptance and migration closure

If Web UAT passes:

- create a final Web cutover acceptance artifact;
- update `STATUS.md`, `MEMORY.md`, `ROADMAP.md`, `plan.md`, README/launch docs, and relevant Godot docs;
- mark Godot Web as the accepted normal presentation;
- keep Canvas as documented fallback through at least the next normal product checkpoint;
- commit/push one tested checkpoint;
- only then resume Iteration 10 — Causal Composition and Situation Chaining.

If Web UAT still fails:

- keep Canvas as normal/rollback presentation;
- preserve the canonical world untouched;
- record exact evidence and remaining defect class;
- continue the bounded presentation debug loop rather than declaring partial success.

## Recommended debugging order

Use this priority order and do not skip ahead because later polish can hide earlier defects:

1. evidence + telemetry;
2. deterministic Web reproduction;
3. spatial continuity / teleport elimination;
4. animation lifetime/action-phase semantics;
5. object/support choreography;
6. Web-specific runtime/delivery hardening;
7. automated regression suite;
8. real living-world UAT;
9. migration closure.

## Expected first hypotheses to test

These are hypotheses, not conclusions:

1. New Web frames may be rebasing interpolation from the previous **canonical endpoint** instead of the currently rendered position, producing visible pops when frame arrival and transition timing overlap.
2. The three-second frame polling interval and fixed 2.6-second route transition may interact poorly with real browser/network jitter or multi-heartbeat locomotion.
3. Many non-looping actions deliberately clamp to their terminal frame; after heartbeat-replay prevention this may leave long canonical commitments looking frozen, so explicit sustained-action phase semantics may be required.
4. Web `HTTPRequest` timing/error behavior may differ enough from native Godot to expose request overlap, delay, or cadence defects not seen in bounded native captures.
5. Some perceived "missing animations" may be correct canonical quiet commitments; telemetry must distinguish actual mapping/clock defects from actions that simply did not occur during the observation window.

Prove or reject each hypothesis with telemetry and deterministic fixtures before adopting a fix.

## Execution findings — 2026-08-29

### Proven root causes / contributing defects

1. **Presentation transition origin defect — PROVEN.** New live transitions were reconstructed from prior canonical-frame position instead of Moss's currently rendered anchor. A frame arriving before the prior 2.6-second transition completed could therefore move the actor instantly back to an old endpoint before starting the next interpolation.
2. **Explore-route omission — PROVEN.** The living world emitted `last_event.action="explore"` with a valid multi-corner canonical route, while `_build_live_route()` accepted route evidence only when the action string was `walk`. This discarded authoritative route geometry for real explore locomotion.
3. **Sustained-action terminal clamp — PROVEN.** Inspect, nudge, groom, stretch, and most other non-walk sequences clamped to their final sprite indefinitely. Combined with correct continuation-heartbeat replay suppression, sustained commitments could spend most of their lifetime visually frozen.
4. **Adapter ordering/observability gap — PROVEN.** Exact duplicates were ignored, but older ticks were not explicitly rejected and request overlap/cadence had no observable state. This was a Web robustness gap even though it has not been proven to be the primary teleport cause.
5. **Canonical-world defect — REJECTED for the observed canary symptoms.** During investigation the canonical API remained healthy and advancing, exposed coherent `terrarium.frame.v1`, and Canvas continued to render the same living world. No world reset, migration, force-step, pacing change, route change, or authority change was used.

### Implemented candidate corrections

- Rebase every subsequent accepted frame from `_current_rendered_anchor()` rather than the previous canonical endpoint.
- Preserve the canonical mapped target as the exact transition endpoint.
- Consume canonical route evidence for both `walk` and `explore`.
- Use bounded presentation-only transition timing derived from observed frame-arrival intervals instead of assuming every response lands exactly at the nominal heartbeat.
- Preserve motion clocks across same-motion continuation heartbeats.
- Add intentional sustain loops for inspect/nudge/groom/stretch and a bounded authored recovery phase when leaving those actions; do not create new canonical actions or commitments.
- Keep carry/sleep/window-watch and other intended stable poses as explicit holds rather than accidental frozen phases.
- Reject duplicate **and older** ticks in the adapter and prevent overlapping `HTTPRequest` starts.
- Expose debug state for frame/request cadence, motion clock, transition clock, route, rendered/current target positions, animation frame, facing, and attachment state.
- Add Web error capture and `no-store` delivery for generated Web assets; add a clear occupied-port preflight to the canary launcher.

### Deterministic evidence / regression status

- `artifacts/godot-art-gate/web-deep-debug/baseline.json` records the failed canary and pre-fix lineage.
- `tools/build_godot_web_debug_fixtures.py` produces a deterministic fixture sequence currently containing 99 valid frame deliveries across movement/corners/interruption, continuation heartbeats, all major Moss actions, carry/place, sleep/wake, atmosphere changes, duplicate ticks, an older tick, and timing jitter cases.
- Focused Godot/Web regression tests pass.
- Full repository tests pass under their normal writable test contract.
- A bounded Godot 4.7.2 Lab parser/import run initially caught two new GDScript typing errors; both were fixed and the rerun completed `RC=0` with no lingering Godot/Xvfb/llvmpipe process.

### Still required before closure

1. Generate the replacement ordinary single-threaded Godot Web export from this source.
2. Run that actual exported `.wasm`/`.pck`/JS payload against the deterministic fixture server in a normal browser.
3. Prove at minimum: acceptance-time continuity, exact canonical arrival endpoints, animated locomotion, route-corner continuity, continuation-heartbeat clock preservation, intended sustain/recovery progression, duplicate/older-tick rejection, carry attachment/place release, sleep/wake support, and absence of recurring browser/Godot/WASM/request errors.
4. Run the same replacement Web build against the living persistent world and complete human ordinary-browser UAT.
5. Only then update migration status to complete; otherwise retain Canvas rollback and keep Iteration 10 blocked.
