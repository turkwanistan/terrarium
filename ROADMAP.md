# Terrarium Product Roadmap

Terrarium develops as a normal product. Repository state, live canonical state, evaluation evidence, and direct UAT override this roadmap when they expose a more important concrete weakness.

The accepted behavior architecture remains **attention + affordances + persistent state + habits + short causal commitments**. After Iteration 7, the highest-value gap is no longer behavioral breadth alone: the simulation is materially ahead of the renderer's capacity for authored visual richness. The roadmap therefore gives the art system room to catch up before deeper object behavior resumes.

See `VISUAL_STYLE_OVERHAUL.md` for the detailed visual migration plan and `ART_DIRECTION.md` for the visual law.

## Accepted Iteration 7 — Situational Events and Environmental Attention

**Status: ACCEPTED.** The world now initiates deterministic bounded opportunities and interruptions rather than leaving Moss as the sole source of activity. The accepted implementation uses `terrarium.situational-events.v1`, selective attention/deferral, rare low-commitment interruption, event-linked engagement, and temporary sunlight affordances while preserving the existing bounded-session model.

Target causal structure:

**event → perception → reaction → decision/engagement → aftermath**

The accepted catalog is moving sunlight, bird outside, rain escalation, thunder, night moth, and leaf/window contact. Events remain canonical opportunities, not mandatory interrupt handlers. Ordinary autonomous behavior still dominates the long-run timeline.

## Accepted Iteration 8A — Visual Grammar and Asset Pipeline

**Status: ACCEPTED.** Terrarium now has a validated `display/art/` source tree, 16×16 / 25×15 static art grammar, palette/material bank, deterministic offscreen asset compilation/cache, generalized scene-layer queue, representative production asset migration, and deterministic production-renderer art-direction fixtures. The seed-1701/tick-10080 semantic frame is unchanged from Iteration 7.

The accepted foundation removes the current procedural-art ceiling before adding more simulation complexity.

The current 400×240 → 800×480 exact pixel pipeline is correct, but most finished art is still directly constructed in `display/web/app.js`. Iteration 8A established a reusable authored-art substrate inside Terrarium itself.

Requirements:

- formalize **16×16 source pixels** as the primary static-world art/composition unit, yielding an exact 25×15 grid at 400×240;
- keep canonical Moss/object movement continuous and hardware-neutral; the art grid must not become an authoritative navigation grid;
- add a text-addressable, deterministic, palette-indexed or palette-addressable pixel-asset format for tiles, props, Moss frames, and environmental art;
- introduce `display/art/` (or an evidence-backed equivalent) as editable art source rather than embedding all finished sprite/tile shapes directly in renderer code;
- validate asset dimensions, palette references, transparency/mask rules, and deterministic parsing;
- precompile/cache assets into offscreen Canvas/atlas structures so runtime performance does not depend on repeatedly interpreting text assets;
- introduce richer material/palette banks built around chromatic shadows, strong local color, warm highlights, and cooler shadow shifts rather than one tiny fixed master palette;
- replace special-case draw order with declarative scene layers and generalized foreground/Y-ordering where appropriate;
- preserve existing semantic frame, spatial authority, behavior, events, habits, replay, and live-runtime ownership;
- add deterministic real-browser art-direction fixture capture covering representative room states and key poses;
- judge objective scale/layer/determinism/temporal correctness mechanically while keeping subjective art quality under human/vision inspection;
- migrate enough representative current art to prove the full pipeline without trying to complete the room redraw in the same iteration.

Success means the renderer can cleanly support hand-authored late-16-bit art without `app.js` itself being the primary sprite/tile authoring tool.

Accepted evidence: `history/2026-08-27-pixel-art-overhaul-iteration8a.md`, `artifacts/pixel-art-overhaul-iteration8a.json`, `artifacts/pixel-art-overhaul-iteration8a-regression-matrix.json`, and snapshot `20260828T020631095429Z-pixel-art-overhaul-iteration8a`.

## Accepted Iteration 8B — Room Recomposition

**Status: ACCEPTED.** The persistent habitat is now recomposed through the authored asset/layer system with richer material palettes, stronger zone silhouettes, layered exterior foliage, controlled asymmetry, preserved open-space readability, canonical history overlays, and real foreground furniture lips. The seed-1701/tick-10080 semantic frame remains unchanged from Iterations 7/8A.

Accepted evidence: `history/2026-08-27-pixel-art-overhaul-iteration8b.md`, `artifacts/pixel-art-overhaul-iteration8b.json`, `artifacts/pixel-art-overhaul-iteration8b-regression-matrix.json`, and snapshot `20260828T023312695923Z-pixel-art-overhaul-iteration8b`.

Historical 8B requirements:

Requirements:

- keep the existing room identity and authoritative zones;
- strengthen silhouettes for window, sleeping nook, rug/open space, collection shelf, activity corner, desk, bowls, and major furniture;
- shift from muted-cozy assumptions toward **richer saturated natural color** while preserving coherent value grouping and no-neon restraint;
- use clustered shading, selective chromatic outlines, readable top/front/recessed planes, and hard contact shadows;
- use controlled organic asymmetry to break grid repetition;
- increase authored foliage/exterior richness through the window;
- concentrate detail around furniture/edges/focal clusters while leaving the rug/open movement field as deliberate visual rest;
- strengthen foreground framing, overhangs, shelf/desk/blanket lips, and other depth cues;
- preserve all authoritative persistent-history marks and make them legible in the new material language;
- compare the complete 800×480 renderer across deterministic lighting/weather/history states, not only isolated assets.

Success means a screenshot with Moss hidden already reads as a deliberate, richly authored late-16-bit life-RPG interior rather than a procedural pixel mockup.

## Accepted Iteration 8C — Moss Sprite Overhaul

**Status: ACCEPTED.** Moss's accepted action presentation now uses 46 authored low-frame pixel assets rather than runtime body/head/leg/tail construction. Four-frame locomotion, object-contact acting, quiet actions, window watch, sleep/curled sleep, and wake all route through the existing authored-art cache. Exact target-dependent forepaw reach remains a bounded presentation detail tied to canonical contact state. Stillness remains valid and no new behavior/action enums were added.

The seed-1701/tick-10080 semantic frame remains `e64af0693418973eab51a4f154c375399331fa4117f8168a083ab9296b9a1102`, unchanged from Iterations 7/8A/8B. All 47 tests, four-seed 10,080-step evaluator matrices, exact 2× raster checks, deterministic repeat, 0 px continuity probe, and RAF pacing gates pass.

Accepted evidence: `history/2026-08-27-pixel-art-overhaul-iteration8c.md`, `artifacts/pixel-art-overhaul-iteration8c.json`, `artifacts/pixel-art-overhaul-iteration8c-regression-matrix.json`, and snapshot `20260828T030258821895Z-pixel-art-overhaul-iteration8c`.

## Accepted Iteration 8D — Object Identity and Stateful Affordances

**Status: ACCEPTED.** The six persistent movable objects now use canonical `terrarium.object-affordances.v1` identity/state rather than one generic interaction graph. Rolling, soft-nesting, delicate, and keepsake archetypes expose different affordance subsets; roll→retrieve, tug→rumple→nest, and handled→displayed produce persistent consequences that change later possibilities.

Object identity remains compact and interpretable: blue stone/acorn are rolling, red thread is soft-nesting, amber leaf is delicate, and shell/glass star are keepsakes. Soft-object tug/nesting is constrained to floor/bed-compatible zones. Object-aware arrangement is a bounded tendency underneath `terrarium.habits.v1`, not a hard destination or new planner.

The renderer now selects **13 authored object-state variants** from canonical state. The full authored manifest is **73 assets**, preserving the accepted 8B room and 46-asset 8C Moss vocabulary. The seed-1701/tick-10080 semantic frame is `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`; unlike 8A–8C, this hash intentionally changes because object archetype/state/available affordances are authoritative frame data.

Acceptance: **49/49 tests**, 36-source Python-3.10 grammar, 73/73 asset validation, 10,080-event technical exact replay, four-seed 10,080-step behavior/spatial/coherence/habit matrices, Iteration-6 repertoire, Iteration-7 situations, dedicated 8D object-affordance evaluation, exact-repeat production-browser UAT, **0 px** continuity, and healthy RAF pacing all pass. Roll→retrieve is 96.15–100%; tug→nest is 85.71–100%; illegal delicate/keepsake nudges are zero.

Accepted evidence: `history/2026-08-28-pixel-art-overhaul-iteration8d.md`, `artifacts/pixel-art-overhaul-iteration8d.json`, `artifacts/pixel-art-overhaul-iteration8d-regression-matrix.json`, and snapshot `20260828T112207258140Z-pixel-art-overhaul-iteration8d`.

## Accepted Iteration 8E — Atmospheric World

**Status: ACCEPTED.** The habitat now has persistent non-commanding ambient presentation derived from canonical time/weather rather than a new simulation subsystem. Five authored environment assets support three window-foliage depth layers, curtain motion, and a nook sconce; renderer timing adds phase-varied foliage, rain/runoff, mist drift, localized light motes, branch shadows, and water shimmer. Night uses hard-edged warm local palette treatment against the cool room, while rain/mist modify the whole-scene finite palette as well as the window.

The implementation is renderer/art/tooling-only: authoritative `terrarium/` source is unchanged and seed-1701/tick-10080 remains `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`, exactly matching accepted 8D. Ambient presentation carries no behavior command, persistent state, planner role, or event semantics.

Acceptance: **51/51 tests**, 37-source Python-3.10 grammar, 78/78 asset validation, dedicated atmosphere evaluation, 10,080-event technical exact replay, all four 10,080-step behavior/spatial/coherence/habit seed matrices, repertoire/situations/object-affordance regressions, exact-repeat 56-second production-browser UAT, **0 px** continuity, exact 2× raster output, and healthy RAF pacing all pass.

Accepted evidence: `history/2026-08-28-pixel-art-overhaul-iteration8e.md`, `artifacts/pixel-art-overhaul-iteration8e.json`, `artifacts/pixel-art-overhaul-iteration8e-regression-matrix.json`, and snapshot `20260828T123835255741Z-pixel-art-overhaul-iteration8e`.

## Accepted Iteration 8F — Seasonal Terrarium

**Status: ACCEPTED.** Terrarium now has canonical `terrarium.seasons.v1` long-horizon state: spring/summer/autumn/winter, each 21 real days, with discrete early/full/late 7-day stages. Existing worlds migrate additively from their first post-upgrade observation rather than receiving fabricated historical seasons; restart and replay remain exact.

Presentation preserves the familiar room while changing long-horizon exterior/palette identity. Five authored environment assets and four finite seasonal palette treatments support spring blossoms/fresh greens, fuller summer canopy, staged autumn thinning/rust foliage, and sparse pale winter branches/exterior. Canonical weather remains independent and composes after season; local warm light remains a final hard-edged treatment. Missing canonical season stays visually neutral. Season does not change Moss behavior or weather/event occurrence in 8F.

Acceptance: **55/55 tests**, 38-source Python-3.10 grammar, 83/83 asset validation, dedicated season evaluation, 10,080-event technical exact replay, all four 10,080-step behavior/spatial/coherence/habit seed matrices, repertoire/situations/object-affordance/atmosphere regressions, exact-repeat multi-season production-browser UAT, **0 px** continuity, exact 2× raster output, healthy RAF pacing, and verified canonical host migration/restart/replay all pass. Seed-1701/tick-10080 semantic frame `51d574524e710025428d615dadfcf48fb30e826a03b7b58126ce54784ea9b6ca` differs from 8E only by top-level `season`.

Accepted evidence: `history/2026-08-28-pixel-art-overhaul-iteration8f.md`, `artifacts/pixel-art-overhaul-iteration8f.json`, `artifacts/pixel-art-overhaul-iteration8f-regression-matrix.json`, and snapshot `20260828T160757100074Z-pixel-art-overhaul-iteration8f`.

## Accepted Iteration 9 — Emergent Situations and Consequence Memory

**Status: ACCEPTED.** Canonical `terrarium.consequence-memory.v1` keeps at most 12 unresolved causal consequences from prior event aftermath, traces, arrangements, displacement, and nesting. The append-only event ledger remains complete history; no generic planner or renderer-side memory was added. Later revisit chains reuse the existing bounded intent/session model: recognize → approach → engage → recover.

Controlled evaluation proves identical immediate visible states with different causal histories can remain equal until a later recognition and then diverge deterministically. Four-seed 10,080-step runs produce sparse delayed revisits without breaking quiet behavior, possessions, object state, situations, habits, atmosphere, or seasons. Canonical migration is neutral and does not fabricate old consequences.

Acceptance: **60/60 tests**, 41-source Python-3.10 grammar, JS syntax, 10,080-event exact replay, four-seed behavior/spatial/coherence/habits, repertoire/situations/object-affordance/atmosphere/season regressions, dedicated consequence evaluator, production browser UAT, and canonical host migration/replay all pass.

Accepted evidence: `history/2026-08-28-pixel-art-overhaul-iteration9.md`, `artifacts/pixel-art-overhaul-iteration9.json`, `artifacts/pixel-art-overhaul-iteration9-regression-matrix.json`, snapshot `20260828T182004989725Z-pixel-art-overhaul-iteration9`.

## Presentation Bridge — Staged Godot Cutover and Live UAT

**Status: CANARY ACTIVE — EXTENDED LIVE UAT PENDING.** Explicit cutover approval was received on 2026-08-29 and Phase A is implemented: `scripts/run_presentation.sh` / `.ps1` now select Godot by default while retaining Canvas as an explicit same-world rollback. This remains an interposed presentation checkpoint before Iteration 10, not a new simulation generation. The canonical Terrarium world/API remains authoritative and the migration is not closed until extended live UAT passes.

Readiness already established:

- approved cleaned Godot room direction and exact authored-geometry/palette-only Moss law;
- all 15 canonical activity names explicitly mapped with dedicated nudge/loaf/groom/stretch and pickup→carry presentation where appropriate;
- 73/73 repository tests and 13/13 focused Godot presentation tests pass at readiness;
- representative native Godot 4.7.2 captures pass under the bounded `GODOT_NATIVE_VALIDATION.md` procedure;
- real-current-frame adapter proof passed through the actual read-only `GET /api/frame` bridge without weakening Lab isolation;
- `scripts/run_godot_live_candidate.sh` attaches to an already-running canonical API, performs no world lifecycle/write operation, refuses accidental headless launch, and blocks llvmpipe unless explicitly overridden;
- Canvas is unchanged and remains the immediate rollback presentation.

### Phase A — reversible canary cutover

**Implemented 2026-08-29.** The default presentation selectors now choose Godot; Canvas remains explicit fallback; world/API lifecycle and renderer hashes remain unchanged. Phase-A regression state is 75/75 repository tests and 15/15 focused Godot presentation tests PASS. Active evidence: `artifacts/godot-art-gate/canary-cutover/cutover.json`.

The implemented contract:

- make Godot the normal presentation choice without changing `terrarium.api.server`, runtime data ownership, heartbeat cadence, database, canonical routes/actions, or world startup;
- keep Canvas launchable through an explicit fallback/rollback path for at least the entire live-UAT checkpoint;
- presentation selector/launcher changes must be independently reversible and must not stop/reset/recreate the canonical world;
- do not regenerate production art during normal presentation startup; generated candidate assets are build/review artifacts, not runtime-mutating state;
- do not run the always-on presentation through Xvfb/llvmpipe on the OptiPlex. Native software-rendered Lab runs remain bounded validation only.

### Phase B — real-world live UAT

Observe the actual persistent world through Godot long enough to cover multiple heartbeat continuations, route transitions, quiet holds, and environmental changes. Prefer one continuous 30–60 minute canary plus targeted deterministic/native probes for rare actions rather than forcing the living simulation to perform test choreography.

Live-UAT acceptance should cover:

- no authored action restarts on repeated continuation heartbeats;
- locomotion/explore, route corners, facing, arrival settle, and no furniture-cut/teleport regression;
- inspect and nudge approach/contact/hold/recover readability;
- pickup→carry attachment, carried travel/turns, place lower/contact/release/recover continuity;
- loaf, groom, stretch, rest, react/orient, and window-watch remain distinct and calm;
- sleep floor-gate→supported curl and wake→exit support choreography remains coherent;
- canonical object identity/state, target ownership, positions, carried state, and interaction aftermath remain read-only presentation inputs;
- time/lighting/weather/season selection stays consistent with canonical frame state;
- no renderer-private behavior/history, no API writes, no database access, and no world-lifecycle coupling;
- no unexpected CPU escalation, runaway Godot process, or renderer process leak.

Use Canvas as a same-world comparison when a suspected Godot bug is ambiguous. A presentation defect may justify a Godot fix; it must not be “fixed” by changing canonical behavior unless independent simulation evidence shows the world itself is wrong.

### Phase C — close the migration

When the canary passes:

- record a cutover acceptance artifact and update `STATUS.md` / launch docs;
- keep Canvas as a documented fallback for the next normal product checkpoint unless evidence supports later retirement;
- stop treating Godot migration as the main project and resume normal Terrarium development;
- proceed to Iteration 10 — Causal Composition and Situation Chaining.

Failure/rollback rule: switch presentation back to Canvas, leave the canonical world process and state untouched, preserve evidence, and fix/revalidate Godot in isolation.

## Iteration 10 — Causal Composition and Situation Chaining

Highest-value next step: compose existing systems rather than widen the action list. A current event/opportunity should sometimes intersect with a stored consequence, object state, habit, arrangement, or spatial condition and create a bounded situation that neither system would create alone.

Requirements:

- multi-cause situations remain canonical, deterministic, explainable, and sparse;
- existing attention/affordance/intent machinery remains the default expression mechanism;
- no scripted quest chains, generic planner, needs/personality stats, dialogue, inventory UI, or LLM action selection;
- chains must release cleanly and ordinary quiet behavior must continue to dominate;
- source provenance must remain compact enough to explain why the situation happened;
- browser presentation should rely on existing authored acting/objects/environment unless UAT proves a concrete legibility gap.

Success means a present event can naturally redirect Moss into an old unresolved part of his world—for example, an outside stimulus draws him through a zone where a previously displaced object becomes relevant—without any prewritten story graph.

## Visual convergence passes

After the structural 8A–8F work, schedule explicit review/redraw passes rather than treating each first implementation as final art.

Useful passes may focus on:

- silhouettes;
- value/color;
- material language;
- density vs negative space;
- Moss charm/acting;
- lighting;
- ambient animation;
- clutter reduction;
- seasonal consistency;
- long-duration observation.

A pass may remove or simplify content. More sprites, pixels, props, or systems do not automatically mean a better image.

## Planning / SBC gate

Do **not** introduce GOAP, a generic planner, Sims-style needs, personality-stat systems, quest logic, or LLM action selection merely because situations become richer.

Do **not** propose a new SBC generation merely because Terrarium needs an art asset pipeline, visual fixture matrix, or project-local renderer tooling. Implement those locally first.

Only propose a more general planning substrate or Self-Building Computer Generation 18 if implementation evidence demonstrates a genuinely reusable limitation that cannot reasonably be expressed or evaluated with Terrarium's existing architecture and promoted SBC capabilities. Product complexity by itself is not a substrate deficiency.
