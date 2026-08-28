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

## Iteration 8F — Seasonal Terrarium

Make long real-world time a visual system.

Requirements:

- add a canonical deterministic seasonal state on a timescale substantially slower than the current 72-real-minute day;
- do not directly reuse a 28-current-world-day season because it would cycle implausibly fast in real time;
- preserve stable room landmarks/geometry across seasons;
- coordinate seasonal palette, exterior foliage, weather/particles, lighting, selected interior accents, and ambient life;
- use spring/summer/autumn/winter as distinct emotional/color states rather than simple recolors;
- keep history/replay/migration deterministic and fail-safe.

Success means returning to the same familiar room after long real-world time reveals a meaningful environmental transformation without erasing place identity.

## Iteration 9 — Emergent Situations and Consequence Memory

Once world events, richer visual state, and stateful object affordances exist, let their consequences compose across longer horizons.

Requirements:

- Moss can revisit, maintain, exploit, or react to consequences created by prior activity;
- prior arrangements, temporary environmental events, object displacement/state, learned habits, and persistent traces can create later opportunities;
- occasional multi-stage situations may unfold across minutes, hours, or days without hard-coded narrative scripts;
- recognition should come from authoritative world state/history rather than hidden planner memory;
- equivalent present worlds with different causal histories should be able to produce meaningfully different future situations while remaining individually deterministic;
- retain bounded intent/session machinery as long as it can express the needed causal chains cleanly.

Example target shape:

> moth appears → Moss follows it → engages a ball → ball rolls under furniture → moth disappears → much later Moss revisits the area and retrieves or re-engages the displaced ball

Success means richer situations emerge from interacting systems rather than from prewritten quest chains.

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
