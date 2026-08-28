# Terrarium Plan

## Completed Gen17 initial scope

### Phase 0 — contracts and skeleton
- deterministic canonical world/state model
- versioned append-only meaningful events with hash chain
- deterministic seed/rule/tick entropy
- SQLite canonical state + immutable snapshots + inspectable JSONL event history
- exact snapshot + subsequent-event replay
- fixed hardware-neutral `terrarium.frame.v1` at exactly 800×480
- persistent world HTTP service; renderer is read-only/disposable

### Phase 1 — something visibly alive
- one autonomous creature (`Moss`)
- idle/walk/explore/rest/sleep/wake/look-outside behavior
- day/night/environment cycle
- multiple named habitat zones
- Canvas interpolation/animation and expressive creature state
- world continues while browser is closed

### Phase 2 — persistent objects
- six persistent objects
- inspect/carry/place interactions
- collection shelf and persistent zones
- visible habitat wear/accumulation
- restart persistence and exact replay of arrangements

## Completed normal product checkpoint — Lived-in staging

The first post-Gen17 product iteration strengthened accumulated-life legibility without adding new mechanics:

- deterministic authored placement slots per habitat zone;
- collision-aware placement so persistent collections do not overlap;
- connected worn routes derived from canonical `path_wear`;
- settled/scuffed cues beneath repeatedly moved possessions;
- `times_inspected` exposed through the semantic frame for later visual storytelling.

Evidence: `history/2026-08-27-lived-in-staging.md`, `artifacts/visual-storytelling-comparison.json`, `artifacts/visual-storytelling-counterfactual.json`, and snapshot `20260827T050435058386Z-lived-in-staging`.

## Completed normal product checkpoint — Activity aftermath

- persistent history-derived counters for sleeping-nook sleep, window-watching, and activity-corner use;
- rumpled/compressed sleeping nook from actual sleep history;
- pane/sill traces from repeated window watching;
- progressively rearranged papers/work marks from activity-corner use;
- same-horizon counterfactual proves legacy frame outcome is unchanged except the new aftermath payload.

Evidence: `history/2026-08-27-activity-aftermath.md`, `artifacts/activity-aftermath-comparison.json`, snapshot `20260827T054359565518Z-activity-aftermath`.

## Completed normal product checkpoint — Temporal aftermath polish

- activity-aftermath counter changes interpolate over 1.8 seconds in the renderer;
- 26 authored aftermath layers fade in progressively instead of appearing through integer count buckets;
- stable hash-derived micro-variation keeps papers/traces organic without `Math.random`;
- persistent window traces respond subtly to rain/mist/clear conditions;
- bedding compression, pillow drift, and creases grow continuously from actual sleep history;
- generic path wear is quieter so activity-specific history retains visual priority;
- the canonical seed-1701/tick-240 frame is unchanged from the previous checkpoint.

Evidence: `history/2026-08-27-temporal-aftermath-polish.md`, `artifacts/temporal-aftermath-polish.json`, snapshot `20260827T115103702156Z-temporal-aftermath-polish`.

## Completed normal product checkpoint — Temporal rendering intelligence

- production renderer continues to use ordinary `requestAnimationFrame`; development mode can render the same Canvas implementation at exact supplied timestamps;
- deterministic source→target frame fixtures cover left/right movement, carried movement, idle control, and rain control;
- machine-readable temporal telemetry records semantic/rendered trajectory, interpolation, facing, pose/activity, carried-object attachment, ambient classes, and compact raster evidence from the actual 800×480 Canvas;
- real RAF pacing is measured separately from manual-clock correctness;
- promoted reusable `temporal-render-auditor-r1` objectively detects teleports, frozen semantic movement, reversals, facing mismatch, whole-scene jitter, carried-object detachment, semantic→visual causality failure, endpoint settling, and RAF stalls;
- independent fixture outcomes were 10/10 correct; Gen14 mutation testing killed 10/10 dangerous mutants with zero survivors;
- genuine Terrarium left/right/carry/idle/rain/RAF tasks passed;
- measured endpoint behavior justified one renderer-only change from cubic smoothstep to quintic smootherstep, reducing sampled endpoint speed from 13.2308% to 2.3047% of peak on the canonical left-walk capture;
- no production CV/video dependency, permanent MCP growth, world-model change, or SBC Gen18 substrate work was required.

Evidence: `history/2026-08-27-temporal-rendering-intelligence.md`, `artifacts/temporal-rendering-intelligence.json`, compact evidence under `artifacts/temporal-audit-inputs/`, snapshot `20260827T125248568567Z-temporal-rendering-intelligence`.

## Evaluation loop

Keep the development loop: implement → deterministic accelerated run → technical/behavior evaluation → deterministic temporal capture where relevant → independent RAF probe where relevant → live browser inspection → identify weakness → bounded change → replay/regression.

Primary invariants/metrics: replay equality; event-chain integrity; restart equality; Python 3.10 syntax compatibility; action diversity/entropy; non-sleep repetition; object pickups/placements/inspections; moved-object count; persistent habitat marks; renderer authority/synchronization; deterministic temporal-capture equality; subject trajectory/facing/attachment/causality; independent real-RAF pacing; event storage growth; and direct visual comparison against the accepted deterministic snapshot timeline.

Use project-factory / Experiment Capsule / counterfactual / Forge capabilities only when a real engineering uncertainty or reusable capability gap justifies them. Do not create Self-Building Computer generations merely because Terrarium advances.

## Next product iteration

Highest-value target: make **present activity and accumulated aftermath feel causally connected**. While Moss sleeps, watches the window, or uses the activity corner, the already-existing traces should respond subtly to the current action/environment without moving authority into the renderer or adding new mechanics. Use the promoted temporal auditor to prove timing/attachment/stability correctness while keeping subjective warmth/charm as human visual judgment.

Objective temporal correctness is now covered. Automated subjective artistic-quality judging remains intentionally out of scope; do not reinterpret temporal metrics as a warmth/charm oracle.

## Later

Only after the software experience is compelling: preferences/routines, richer long-term identity, optional interaction/conversation, and hardware renderer experiments. Hardware must remain a renderer/client of the same host-owned creature and history.

## Checkpoint discipline

For each meaningful user-visible iteration: implement → test/evaluate → run/inspect → capture one deterministic development snapshot → update `STATUS.md` / history → commit → push attempt. Avoid snapshotting every small edit and never commit the live SQLite/event ledger. Git is product-development history, not a backup of Moss's living state.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 1

- replaced the smooth storybook/vector-like presentation with a true 400×240 pixel-native Canvas art surface;
- exact 2× nearest-neighbor presentation preserves the fixed 800×480 reference contract without changing canonical semantic coordinates;
- rebuilt Moss as a brown floppy-eared gameplay sprite with side/three-quarter orientation, no default glasses, and pixel key poses for the existing action vocabulary;
- rebuilt the core room with clustered stepped shading, selective outlines, moss/walnut/amber/dusty-blue/cream palette families, hard-edged depth, and persistent-history marks;
- moved day/dawn/dusk/night/rain/mist presentation to finite palette/value steps and sparse pixel effects;
- preserved canonical action commitments, targets, contact/attachment/place/sleep semantics, 72-minute day, ~9-minute weather blocks, and calm decision cadence;
- proved exact raster scaling across 16 deterministic real-browser scenarios / 176 sampled frames with zero scale errors;
- the original promoted temporal auditor exposed a valid integer-grid endpoint-settling coverage gap;
- existing Capability Forge produced promoted `grid-quantized-temporal-render-auditor-r1` (`57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`), preserving the original 10/10 oracle and killing 2/2 dangerous Gen14 mutants;
- no SBC substrate change or Gen18 work was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration1.md`, `artifacts/pixel-art-overhaul-iteration1.json`, snapshot `20260827T183924459328Z-pixel-art-overhaul-iteration1`.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 2

- replaced generic/procedural Moss deformation with explicit authored key-pose acting for the existing action vocabulary;
- established a four-frame planted-foot walk with ear/tail response and discrete target-contact poses;
- strengthened window, bed, rug, shelf, desk, bowls, floor/wall materials, furniture supports, occlusion, and hard grounding shadows;
- kept persistent-history marks authoritative and made rain/ambient detail sparser and more deliberate;
- preserved semantic seed-1701/tick-698 frame SHA `7edb823cf657ff72ba96c6f6cf38fe45a547760b8bf4c5e0eb534372c6c4fa6c`;
- passed 17-scenario/187-frame deterministic browser evaluation, 9/9 promoted grid-aware temporal audit, exact replay, behavior regression, RAF, and human 800×480 inspection;
- no capability forge or Gen18 work was needed.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration2.md`, `artifacts/pixel-art-overhaul-iteration2.json`, snapshot `20260827T192116263284Z-pixel-art-overhaul-iteration2`.

## Next product iteration

Choose the next normal Terrarium target from direct UAT. If the remaining objection is visual craft, continue art refinement within the accepted pixel contract. If Moss still enters furniture, traverses implausible surfaces, or chooses inappropriate rest/sleep locations, make that a separate **spatial navigation and habitat-affordance** iteration with explicit semantic evaluation rather than disguising behavior changes as renderer polish.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 3

- introduced `terrarium.spatial.v1` with authored walkable bounds, major furniture blockers, route nodes, zone approaches, contact points, and supported sleep geometry;
- replaced arbitrary straight interpolation with deterministic blocker-safe authoritative route polylines;
- separated semantic object/zone targets from physical approach and contact positions;
- made sleep always use the supported bed anchor and made wake explicitly exit through the bed gate;
- moved shelf, desk, and window zone anchors onto believable usable floor while preserving persisted object history;
- updated future placement slots to accessible tray/work-surface locations;
- made the pixel renderer interpolate authoritative multi-segment routes and face route segments without increasing behavior-decision frequency;
- fixed carried-object attachment continuity across route turns;
- added small art affordances (window perch, collection tray, foreground lips) without replacing the Iteration-2 art direction;
- added Terrarium-specific deterministic spatial evaluation rather than forging a general navigation auditor;
- passed 26/26 tests, technical/behavior/spatial evaluators, exact replay, promoted behavior audit, applicable grid temporal audits, continuity, RAF, deterministic repeat, and real 800×480 inspection;
- no SBC platform changes, Capability Forge work, or Gen18 were required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration3.md`, `artifacts/pixel-art-overhaul-iteration3.json`, snapshot `20260827T204232352544Z-pixel-art-overhaul-iteration3`.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 4

- added bounded `terrarium.behavior-context.v1` recent-zone/recent-object memory plus one short-horizon intent;
- made travel a consequence of context and inhibited recent-zone ping-pong rather than merely lowering a global walk probability;
- established readable arrival, window, object, post-place, sleep, and wake continuations;
- committed carried objects to one delivery destination and preserved same-object continuity from inspect→pickup→delivery→place;
- lengthened calm dwell/recovery commitments without changing the 3-second heartbeat or 72-real-minute day;
- added a Terrarium-specific deterministic coherence evaluator plus multi-seed robustness coverage;
- preserved `terrarium.spatial.v1`, exact replay/restart, canonical-state migration, pixel rendering, and renderer authority boundaries;
- passed 28/28 tests and all technical/behavior/spatial/coherence gates, with fresh real-browser RAF temporal audit;
- no SBC platform change, capability forge, MCP growth, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration4.md`, `artifacts/pixel-art-overhaul-iteration4.json`, snapshot `20260827T212849313774Z-pixel-art-overhaul-iteration4`.

## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 5

- added bounded persistent `terrarium.habits.v1` zone, object, and dawn/day/dusk/night contextual affinities learned from actual experience;
- kept the model compact and interpretable rather than adding needs bars, personality labels, schedules, a general planner, or an LLM layer;
- used saturating reinforcement, slight decay, normalization, slow maturity, exploration floors, and existing recent-history inhibition to prevent lock-in;
- preserved the accepted Iteration-4 RNG stream so migration does not gratuitously reroll behavior before habits mature;
- added conservative neutral migration for existing worlds without replacing Moss, possessions, routine context, object history, or the event ledger;
- added deterministic multi-seed long-horizon evaluation plus equivalent-physical-state / different-history divergence tests;
- passed 33/33 tests and all technical/behavior/spatial/coherence/habit gates, with real 800×480 day-2/day-5/day-7 browser fixture UAT;
- renderer code remained byte-identical; no SBC platform change, Capability Forge work, MCP growth, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration5.md`, `artifacts/pixel-art-overhaul-iteration5.json`, snapshot `20260827T222822886488Z-pixel-art-overhaul-iteration5`.

## Next product iteration

Choose from direct canonical-runtime UAT after deployment. Let actual observation decide whether the next maturity target is richer expression of learned habits, longer-lived environmental consequences, or another concrete product weakness. Do not invent a new generation or generic planning layer by cadence.


## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 6

- audited ten action labels down to seven genuinely distinct Iteration-5 semantic families before adding new behavior;
- added authoritative object `nudge` with persistent displacement, causal re-inspection, and readable paw-contact→slide→settle rendering;
- added bounded `loaf`, `groom`, `stretch`, and environmental `react` activities with calm commitments rather than fidget loops;
- expanded carry/place into habit-shaped personal-space arrangement across plausible authored zones instead of a mostly shelf-directed loop;
- added additive `terrarium.affordances.v1` completion/nudge/comfort/arrangement history with neutral migration and no fabricated pre-upgrade activity;
- repaired the deterministic weather function so canonical seed 1701 actually experiences clear/rain/mist opportunities;
- increased meaningful families **7→10**, long-run family entropy to **2.915–2.946 bits**, and cut generic-behavior share to **58.2–60.5%** across seeds 1701/1702/42/999;
- proved controlled histories deterministically diverge through the new affordance space, including loaf patterns and persistent object arrangements;
- passed 39/39 tests, Python-3.10 grammar, JS syntax, technical/behavior/spatial gates, four-seed coherence/habit/repertoire matrices, and real 800×480 temporal UAT;
- no SBC platform change, Capability Forge work, MCP growth, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration6.md`, `artifacts/pixel-art-overhaul-iteration6.json`, snapshot `20260827T233841118223Z-pixel-art-overhaul-iteration6`.

## Planned product roadmap after Iteration 6

> Historical note: this sequence was correct before the post-Iteration-7 visual-gap audit. The current forward sequence is the 8A–8F visual overhaul below and in `ROADMAP.md`.

The explicit forward roadmap now lives in `ROADMAP.md`:

1. **Iteration 7 — Situational Events and Environmental Attention:** world events become canonical opportunities/interruptions with the causal shape **event → perception → reaction → decision/engagement → aftermath**.
2. **Iteration 8 — Object Identity and Stateful Affordances:** object classes expose materially different affordance subsets and persistent state transitions rather than sharing one generic interaction graph.
3. **Iteration 9 — Emergent Situations and Consequence Memory:** events, object state, arrangements, and habits compose into later opportunities across minutes/hours/days without scripted narrative chains.

Direct canonical-runtime UAT may reprioritize this sequence if it exposes a more severe concrete weakness. Do not add GOAP, generic planning, needs/personality-stat systems, quest logic, or LLM action selection by default. Only revisit the planning/SBC substrate if implementation evidence shows the existing attention + affordance + persistent-state + habit + bounded-session model cannot express the required causal situations cleanly.


## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 7

- added canonical deterministic `terrarium.situational-events.v1` with six bounded event types: moving sunlight, bird, rain intensification, thunder, night moth, and leaf/window contact;
- made event occurrence/lifecycle, source coordinates, salience, attention status, and temporary affordances authoritative world state rather than renderer inventions;
- added selective ignore/orient/defer/rare-interrupt/approach/engage/recovery behavior using the existing bounded intent/session model rather than a planner;
- protected high-commitment manipulation, possession continuity, supported sleep, spatial authority, learned habits, and ordinary calm behavior from mandatory interruption;
- added moving sunlight as a temporary walkable/loafable canonical affordance that can shift and expire;
- kept window event source coordinates separate from physically valid Moss engagement anchors;
- tuned deterministic per-type cooldowns so all six event types recur without visual clustering;
- preserved Iteration-6 repertoire and long-horizon habit divergence without weakening anti-lock-in thresholds;
- added deterministic four-seed situational evaluation plus final actual-browser fixtures for sunlight engagement, bird engagement, thunder reaction, moth engagement, and deliberate non-reaction;
- passed 43/43 tests, Python-3.10 grammar, JS syntax, technical/replay, four-seed behavior/spatial/coherence/habit/repertoire/situational matrices, and final 800×480 browser UAT;
- no SBC platform change, Capability Forge work, MCP growth, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration7.md`, `artifacts/pixel-art-overhaul-iteration7.json`, snapshot `20260828T010131008922Z-pixel-art-overhaul-iteration7`.

## Next product iteration after Iteration 7

**Iteration 8A — Visual Grammar and Asset Pipeline.** The accepted behavior simulation is currently ahead of the art system. Before adding deeper object mechanics, remove the renderer's procedural-art ceiling by establishing a text-addressable authored pixel-asset pipeline, 16×16 static-world art grammar, richer palette/material banks, declarative scene layers, generalized occlusion/Y-ordering, caching, and deterministic visual-review fixtures.

Do not change Moss intelligence, event semantics, object-affordance behavior, canonical navigation, or the living runtime merely to prove the art pipeline. Migrate enough representative room/Moss/object content to demonstrate that the new asset system can render the existing authoritative frame cleanly and deterministically.

Detailed sequence and acceptance criteria live in `VISUAL_STYLE_OVERHAUL.md`.

## Updated visual overhaul sequence

1. **8A — Visual Grammar and Asset Pipeline**
2. **8B — Room Recomposition**
3. **8C — Moss Sprite Overhaul**
4. **8D — Object Identity and Stateful Affordances**
5. **8E — Atmospheric World**
6. **8F — Seasonal Terrarium**
7. **9 — Emergent Situations and Consequence Memory**

The sequencing intentionally lets renderer/art capability catch up before expanding the simulation further. Later art-convergence passes may redraw, simplify, or remove assets; progress is not measured by feature count.


## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 8A

- established `display/art/` as the editable source of truth for authored recurring pixel clusters;
- formalized the 16×16 static-world grammar on the exact 400×240 / 25×15 art surface without changing continuous semantic coordinates;
- added validated palette-addressed `terrarium.pixel-asset.v1` assets plus a material/palette bank;
- moved palette definitions out of `app.js` and added deterministic asset preload, offscreen compilation, and `asset@palette` caching;
- introduced the declarative `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT / ALWAYS_FRONT` scene queue with stable Y/base ordering;
- migrated a representative floor tile, collection shelf, water bowl, Moss idle frame, and desk plant through the production pipeline while preserving legacy coexistence;
- added deterministic production-renderer art-direction fixtures covering time, weather, history, Moss activity, and situational events;
- preserved the Iteration-7 semantic seed-1701/tick-10080 frame byte-for-byte by hash;
- passed 45/45 tests, Python-3.10 grammar, JavaScript syntax, exact replay/technical checks, four-seed behavior/spatial/coherence/habit regressions, repertoire/situational regressions, deterministic browser raster checks, zero-jump continuity, and clean RAF pacing;
- used an isolated `/tmp` development world; canonical Moss was not reset or replaced;
- no SBC platform change, Capability Forge work, frozen MCP change, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration8a.md`, `artifacts/pixel-art-overhaul-iteration8a.json`, `artifacts/pixel-art-overhaul-iteration8a-regression-matrix.json`, snapshot `20260828T020631095429Z-pixel-art-overhaul-iteration8a`.

## Next product iteration after Iteration 8A

**Iteration 8B — Room Recomposition.** Use the accepted authored-art substrate to redraw the habitat itself: richer saturated natural palette behavior, stronger zone/furniture silhouettes, more specific material language, controlled asymmetry, richer window/exterior foliage, foreground framing/depth, and preserved quiet rug/open-space readability. Keep history marks canonical and spatially valid. The complete Moss action-sprite migration remains Iteration 8C.


## Completed normal product checkpoint — Pixel-Art Overhaul, Iteration 8B

- recomposed the habitat's major static visual masses through the accepted authored-art pipeline rather than continuing to grow room-specific procedural drawing code;
- expanded the manifest from 5 to **15 authored assets**, adding the room shell, window exterior/alcove, sleeping nook, living rug, activity desk, food bowl, and dedicated foreground lips;
- redesigned dawn/day/dusk/night material palettes toward richer saturated-natural color with deeper timber, stronger vegetation, distinct cloth, terracotta, glass-light, stone and brass roles;
- strengthened zone identity, furniture silhouettes, controlled asymmetry, exterior foliage, focal detail density, and foreground depth while deliberately preserving the broad rug/open movement field;
- split production room composition across `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT` rather than treating the whole room as one background pass;
- preserved canonical path wear, bedding aftermath, activity clutter, window marks, situational-event presentation, continuous spatial coordinates, object placement and Moss navigation;
- preserved the Iteration-7/8A seed-1701/tick-10080 semantic frame byte-for-byte by hash;
- passed **46/46 tests**, Python-3.10 grammar, JavaScript syntax, authored-art validation, exact replay/technical checks, four-seed 10,080-step behavior/spatial/coherence/habit regressions, repertoire/situational regressions, exact-2× browser raster checks, zero-jump continuity, deterministic repeat and clean RAF pacing;
- used isolated `/tmp/terrarium-iteration8b-uat`; canonical Moss was not reset or replaced;
- no SBC platform change, Capability Forge work, frozen MCP change, or Gen18 was required.

Evidence: `history/2026-08-27-pixel-art-overhaul-iteration8b.md`, `artifacts/pixel-art-overhaul-iteration8b.json`, `artifacts/pixel-art-overhaul-iteration8b-regression-matrix.json`, snapshot `20260828T023312695923Z-pixel-art-overhaul-iteration8b`.

## Next product iteration after Iteration 8B

**Iteration 8C — Moss Sprite Overhaul.** The recomposed room now makes Moss's remaining procedural body-part/action rendering the clearest visual bottleneck. Replace those poses with true authored low-frame sprites while preserving the current semantic action vocabulary, timing, target/contact authority, possession continuity, routes, habits, and situational-event behavior. Keep stillness valid; do not add random fidgets or a smooth skeletal animation system.
