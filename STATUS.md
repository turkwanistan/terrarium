# Terrarium status

## Godot presentation canary — browser delivery prepared, generated web build + live UAT pending

### Visual Convergence 1 — palette-only Moss approved and natively validated

The approved room has completed a bounded artifact-cleanup pass: broad procedural plaster peppering and several regular single-pixel accent fields were replaced with sparse connected material marks while projection, composition, furniture layout, palette/material hierarchy, detail density, 400×240 source art, and exact 2× presentation remain locked. Native Godot 4.7.2 spring/day, rain, and warm-night captures retain the cleaned room direction.

Moss is now locked to **authored geometry → Godot palette only**. The accepted `display/art/moss/*.json` geometry is the production anatomy for every pose; generation translates authored palette roles through `MOSS_MAP` and performs no additive facial/chest/fur finishing, pose-safe recoloring, silhouette expansion, or anatomy edits. Review Candidates A/B/C remain historical comparison evidence only and are not production states.

Production idle is `b76ab00cfaa8cd22976df443ccef70b1ebe9ee13b22e521dfca52760d7fdc65b`. The complete production Moss set now contains 50 top-level rasters with tree hash `60ee1774e3d890fadee4783f896e36c117ae0abb3e1334ac4c20c278758a4f86`. A repository regression test enforces byte-for-byte equivalence between every production Moss PNG and its authored JSON geometry translated through `MOSS_MAP` only.

Native Godot 4.7.2 representative validation passes spring idle, walk, inspect contact, sleep settle/curled, wake exit, carry, place contact/release, window-watch, rain idle, and warm-night idle. Across spring/rain/night idle, the promotion changes 636 rendered pixels per frame and every changed pixel stays inside Moss's expected actor rectangle; room/background/foreground pixels remain unchanged. Evidence: `artifacts/godot-art-gate/moss-palette-only-promotion/native-validation.json`.

Native validation now follows `GODOT_NATIVE_VALIDATION.md`: one capture per process, a 20-second hard timeout with forced cleanup, orphan/process and guest-load checks after every capture, no blind reruns after tunnel failures, and no large llvmpipe batch capture loops. This policy was added after a runaway Lab batch drove host QEMU CPU extremely high; the bounded validation run completed with no lingering Godot/Xvfb process and final guest load average `0.00 / 0.06 / 0.04`.

### Action Completeness + Canonical Mapping — PASS

The Godot candidate now explicitly covers all 15 canonical activity names used by `WorldEngine.COMMITMENT_TICKS`: idle, rest, walk, explore, inspect, carry, place, nudge, loaf, groom, stretch, react, look_outside, sleep, and wake. `explore` maps to locomotion; `react` maps to the bounded look/orient presentation; `look_outside` maps to window-watch. Compatibility aliases `orient` and `window_watch` remain presentation-only.

The previously collapsed actions now use their accepted authored source geometry directly: nudge gets anticipate/contact/press/hold/recover; loaf gets its distinct relaxed silhouette; groom gets start/contact/hold/recover; stretch gets ready/extend/hold/recover. Canonical `carry` now stages the authored pickup anticipation/contact/lift/hold sequence once before settling into the carry pose. There is deliberately no new canonical `pickup` activity or state.

Live motion timing is now decoupled from per-frame route interpolation. A canonical heartbeat that continues the same motion no longer resets the authored action sequence; a motion change resets the motion clock. This closes the heartbeat-replay defect without changing canonical pacing, routes, behavior commitments, or world state.

Native Godot 4.7.2 one-shot validation passed nudge press, loaf, groom hold, stretch hold, pickup contact/lift, and settled carry. The safety policy caught one initial parse failure before capture (`Variant` inference warning treated as error), terminated the process at the hard timeout, and prevented further work until the line was explicitly typed and a clean Godot editor parse/import gate passed. The subsequent 7/7 captures exited cleanly; final Lab load was `0.00 / 0.02 / 0.00` with no Godot/Xvfb or review-server process left behind. Evidence: `artifacts/godot-art-gate/action-completeness/native-validation.json`.

The presentation-only Godot candidate under `display/godot_reference_v2/` has passed its adoption gate. The approved pre-regression full-room Reference-v2 style is locked, the rejected frontal/chest-forward Moss experiment is removed, and the full production Moss vocabulary now covers idle, walk/explore, inspect, nudge, rest, loaf, groom, stretch, sleep, wake, pickup→carry presentation, place, look/orient, and window-watch.

Visible presentation validation includes spring/day, rain, and warm-night full-room variants; action-scoped bed occlusion with floor-gate → climb → supported curl → wake/exit choreography; canonical route interpolation without teleporting or furniture cuts; and carry/place rendering for all six persistent canonical object identities across their authored interaction states.

The Godot path remains subordinate to the canonical Terrarium simulation. Its live adapter is read-only `GET /api/frame`: canonical state owns Moss position, facing, activity, object identity/state, time, weather, route, and world history. Godot owns only presentation mapping, staging, interpolation, sprite selection, and compositing. It contains no simulation stepping, planner, state writer, or duplicate world authority.

A real-current-frame integration proof now also passes without weakening Lab isolation. A presentation-relevant projection of canonical live tick **113069** (`spring / early`, clear day, Moss `look_outside` at the window) was copied into the isolated Lab and served only on Lab loopback. Native Godot fetched it through the actual `TerrariumReferenceFrameAdapter` `GET /api/frame` path and correctly rendered `spring_day / window_watch` at 800×480. Evidence: `artifacts/godot-art-gate/live-snapshot-integration/native-validation.json`.

Explicit cutover approval was received on 2026-08-29. The first reversible selector checkpoint chose native Godot, but direct UAT clarified the intended product experience: **Terrarium should open as a webpage, without installing Godot or cloning the repository onto the viewing PC.** The canary delivery target is therefore now Godot Web while preserving the same accepted Godot art/runtime logic and world-authority boundary.

Browser-delivery source is prepared. `display/godot_reference_v2/export_presets.cfg` defines a single-threaded, no-extension Web export. In Web builds, `main.gd` automatically enters live read-only mode and derives the canonical API origin from `window.location.origin`; native `--live --api-url` behavior remains available and explicit overrides still win. `.github/workflows/build-godot-web.yml` pins Godot 4.7.2 plus official release hashes and will generate `display/web/godot/` outside the living host, so normal startup never downloads a compiler, regenerates art, or requires Godot on the viewing PC.

Because Godot Web expects a secure browser context for remote delivery, `scripts/run_godot_web_canary.sh` + `tools/godot_web_gateway.py` provide a presentation-only HTTPS boundary. The gateway serves the generated Web payload and proxies only `GET /api/frame` and `GET /api/health` to the already-running canonical HTTP service. POST/PUT/PATCH/DELETE are rejected, `/api/step` is not exposed, and the entry page returns 503 if a real `terrarium.frame.v1` cannot be obtained. `terrarium.api.server`, `run_lan.sh`, the database, heartbeat cadence, canonical routes/actions, and Canvas renderer remain unchanged.

`scripts/run_presentation.sh` now treats **Godot Web as the normal canary mode**, with `--native` retaining the previously validated desktop client and `--canvas` retaining immediate same-world rollback. The Windows-native selector remains optional development plumbing; it is no longer a prerequisite for normal use.

**Canary status:** `SOURCE_READY_AWAITING_GENERATED_WEB_PAYLOAD`. **Migration status:** not closed. The GitHub-generated Web payload has not yet been produced/pulled into the OptiPlex checkout, so no claim of browser-render acceptance is made yet. Once the payload lands, start the HTTPS gateway on the OptiPlex and perform the same extended living-world UAT in an ordinary browser.

**Next execution boundary:** push this source checkpoint, let the pinned GitHub workflow generate `display/web/godot/`, pull that generated commit, then run the browser canary. Canvas stays available throughout. Only after browser live UAT passes should the migration close and Iteration 10 resume.
Historical readiness record: `artifacts/godot-art-gate/cutover-readiness/readiness.json`. Historical native-selector canary: `artifacts/godot-art-gate/canary-cutover/cutover.json`. Current browser-delivery readiness: `artifacts/godot-art-gate/web-cutover/readiness.json`.

Review surface: `artifacts/godot-art-gate/reference-v3-review.html`. Acceptance evidence: `artifacts/godot-art-gate/reference-v3-adoption-gate.json`. Character law: `MOSS_SPEC.md`.

Current validation after browser-delivery preparation: **79/79 repository tests PASS**, **18/18 focused Godot presentation tests PASS**, **1/1 gateway integration test PASS** (19/19 combined), exact authored-geometry Moss regression **PASS**, and generated-art determinism **PASS**. A bounded Godot 4.7.2 headless editor parse of the new Web bootstrap passed in isolated Lab with no lingering Godot/Xvfb process; no new native capture batch was required or run. The HTTPS gateway also passed an end-to-end TLS smoke test covering root delivery, `application/wasm`, canonical frame proxying, and write rejection.

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 9: Emergent Situations and Consequence Memory**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-28-pixel-art-overhaul-iteration9.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration9.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration9-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration9-browser-uat.json`
- consequence evaluator: `artifacts/pixel-art-overhaul-iteration9-consequences.json`
- accepted snapshot: `20260828T182004989725Z-pixel-art-overhaul-iteration9`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `33cced839bb3c2067da01b786c705bf5e3a2a645086e4cfdabee3748ee93f17a`
- renderer JS SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art tree SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`
- behavior rules: `terrarium-rules-v9-consequence-memory`
- consequence schema: `terrarium.consequence-memory.v1`

## What Iteration 9 changed

A bounded canonical causal index now remembers unresolved consequences from situational aftermath, persistent traces, arrangements, displacement, and nesting. It is capped at 12 hot entries and does not replace or scan the full append-only event ledger on every decision. Equivalent visible worlds may carry different authoritative causal histories and later diverge while remaining individually deterministic.

A later opportunity reuses existing behavior machinery: recognize (`react`) → ordinary route/approach (`walk`) → engage (`inspect` / `loaf` / `rest` / `look_outside`) → bounded recovery. One unresolved consequence produces at most one revisit; equivalent new causes reinforce/merge before resolution rather than creating permanent loops.

## Canonical deployment

The accepted code runs against the existing user-owned `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` world. No database reset/replacement occurred.

Post-deploy verification:

- original `created_at`: **2026-08-27T03:45:50.032660Z** preserved;
- rules: `terrarium-rules-v9-consequence-memory`;
- consequence migration: `neutral-existing-world`; no fabricated entries/counters;
- existing season epoch: **2026-08-28T16:33:07.468419Z** preserved;
- season/stage: **spring / early**;
- tick/event: **80,715 / 80,715**;
- exact replay: **PASS**;
- canonical/replayed state SHA256: `e6e5c57d8c49444831a1b765f70e01c31221b9fba9a50138a60a2b344eeb76b3`.

## Validation

- pytest: **60/60 PASS**;
- Python-3.10 grammar: **41 sources PASS**;
- JavaScript syntax: **PASS**;
- technical exact replay at 10,080 events: **PASS**;
- behavior/spatial/coherence/habits: seeds **1701 / 1702 / 42 / 999**, 10,080 each: **PASS**;
- repertoire / situations / object-affordances / atmosphere / seasons: **PASS**;
- dedicated four-seed consequence evaluator: **PASS**;
- controlled same-present/different-history future divergence: **PASS**, divergence tick **627**;
- hot consequence memory bounded at **12**: **PASS**;
- production renderer UAT of recognize→approach→engage: **PASS**.

## SBC conclusion

No reusable substrate deficiency was found. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified. **Gen18: NO.**

## Next: Iteration 10 — Causal Composition and Situation Chaining

Use the systems already present rather than adding another planner layer: allow a current event/opportunity to intersect with a stored consequence, object state, habit, or spatial condition so multi-cause situations emerge. Keep chains bounded, deterministic, explainable, and sparse.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`).

## Godot Web deep-debug status — 2026-08-29

The first ordinary-browser Godot Web canary remains **failed / migration open** because human UAT observed visible Moss teleports and apparently missing/frozen authored animation. Canvas remains the same-world fallback and the persistent canonical world has continued uninterrupted.

Proven findings from the deep-debug pass so far:

- the canonical world was independently healthy while debugging (`/api/health` tick/events advancing; canonical `terrarium.frame.v1` readable);
- live Godot route construction was starting from prior canonical-frame state rather than the actor's currently rendered presentation position, which can create an acceptance-time pop when a new frame arrives mid-transition;
- canonical `explore` events carry valid route evidence, but the old Godot route builder consumed route points only for `walk`, discarding real explore routes;
- non-walk authored actions generally clamped to their terminal frame, which made sustained commitments appear frozen after continuation-heartbeat replay was correctly suppressed;
- the live frame adapter suppressed exact duplicate ticks but did not explicitly reject older/out-of-order ticks and did not expose request-overlap/cadence telemetry.

The candidate fix is presentation-only: rebase each accepted transition from the current rendered Moss anchor while retaining the canonical mapped endpoint and route; consume both `walk` and `explore` routes; derive a bounded transition duration from actual frame-arrival cadence; reject duplicate/older ticks; guard overlapping HTTP requests; and give inspect/nudge/groom/stretch explicit authored sustain loops plus bounded recovery without restarting anticipation on continuation heartbeats. Carry, sleep, and other intended stable holds remain deliberate holds.

Instrumentation now exposes canonical frame arrival, request cadence/state, selected and rendered motion, motion and transition clocks, mapped route, rendered anchor, target anchor, animation frame, facing, and carried-object attachment. A deterministic 99-delivery valid-frame fixture pack covers route corners, interrupted transitions, short/long timing, continuation heartbeats, major activities, carry/place, sleep/wake, atmosphere changes, duplicate ticks, and an older tick.

Validation completed so far:

- focused Godot/Web tests: PASS;
- full repository suite: PASS (second run with the normal writable test contract; the first read-only run failed only because two existing tests intentionally write generated/snapshot output);
- bounded Godot 4.7.2 parser/import gate in `mcp-lab`: PASS after fixing two GDScript Variant-inference errors caught by the first parse;
- post-validation Lab process check: no Godot/Xvfb/xvfb-run/llvmpipe process remained.

Remaining release gates: generate the replacement ordinary exported-Web payload, run the actual `.wasm`/`.pck`/JS build against the deterministic fixture server in a browser and prove continuity/animation/request invariants, then run ordinary-browser UAT against the living world. Iteration 10 remains blocked until this migration gate is closed or deliberately deferred.
