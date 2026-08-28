# Terrarium Product Roadmap

Terrarium develops as a normal product. Repository state, live canonical state, evaluation evidence, and direct UAT override this roadmap when they expose a more important concrete weakness.

The accepted behavior architecture remains **attention + affordances + persistent state + habits + short causal commitments**. After Iteration 7, the highest-value gap is no longer behavioral breadth alone: the simulation is materially ahead of the renderer's capacity for authored visual richness. The roadmap therefore gives the art system room to catch up before deeper object behavior resumes.

See `VISUAL_STYLE_OVERHAUL.md` for the detailed visual migration plan and `ART_DIRECTION.md` for the visual law.

## Accepted Iteration 7 — Situational Events and Environmental Attention

**Status: ACCEPTED.** The world now initiates deterministic bounded opportunities and interruptions rather than leaving Moss as the sole source of activity. The accepted implementation uses `terrarium.situational-events.v1`, selective attention/deferral, rare low-commitment interruption, event-linked engagement, and temporary sunlight affordances while preserving the existing bounded-session model.

Target causal structure:

**event → perception → reaction → decision/engagement → aftermath**

The accepted catalog is moving sunlight, bird outside, rain escalation, thunder, night moth, and leaf/window contact. Events remain canonical opportunities, not mandatory interrupt handlers. Ordinary autonomous behavior still dominates the long-run timeline.

## Next: Iteration 8A — Visual Grammar and Asset Pipeline

Remove the current procedural-art ceiling before adding more simulation complexity.

The current 400×240 → 800×480 exact pixel pipeline is correct, but most finished art is still directly constructed in `display/web/app.js`. Iteration 8A should establish a reusable authored-art substrate inside Terrarium itself.

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

## Iteration 8B — Room Recomposition

Redraw the persistent habitat using the new authored asset/layer system.

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

## Iteration 8C — Moss Sprite Overhaul

Replace Moss's procedural body-part assembly with true authored low-frame sprite acting while preserving current semantic action and timing authority.

Requirements:

- retain Moss's existing hero scale unless visual evidence justifies a bounded revision;
- author strong silhouettes for idle, four-frame walk, inspect, nudge, pickup, carry, place, loaf, groom, stretch, react, window watch, sleep transition, curled sleep, and wake;
- preserve floppy asymmetrical ears, compact body, readable muzzle/head direction, planted feet, expressive but restrained tail, and clear contact poses;
- emphasize pose selection and frame timing over frame count;
- keep stillness valid; no random fidget layer or smooth skeletal tween system;
- keep all target/object/world decisions canonical.

Success means Moss looks like a hand-authored character who belongs to the room, not a set of renderer primitives approximating a dog.

## Iteration 8D — Object Identity and Stateful Affordances

This is the previously planned Iteration 8, deliberately postponed until the visual system can make state differences meaningful.

Requirements:

- define a small set of object classes/archetypes whose available affordances differ materially;
- object-specific affordance subsets replace a universal interaction graph;
- interactions produce authoritative persistent state transitions that affect later possibilities;
- pair those states with authored visual variants so object history is visible rather than only stored;
- candidate archetypes include rolling/chaseable objects, cloth/cushion nesting objects, paper/scatter objects, containers/hiding objects, and plant/reactive environmental objects;
- candidate chains include paw→roll→chase→lost/retrieved, tug→drag→rumple→sleep-on, scatter→pile, peer-into→hide/store, or sniff/watch→fallen-leaf reaction;
- preserve spatial authority, object identity, replay, migration safety, habits, and renderer authority boundaries;
- evaluate combinatorial affordance breadth, state-transition validity, object-class differentiation, long-run persistence, and absence of generic-object collapse.

Success means object identity materially changes both what situations are possible and what the habitat visibly remembers.

## Iteration 8E — Atmospheric World

Make the habitat visibly alive even when Moss is still, without turning the screen into a particle show or making every environmental motion behaviorally significant.

Requirements:

- add a persistent **non-commanding ambient-life** layer distinct from situational events;
- candidate motion includes exterior foliage, curtain movement, pane runoff, leaf drift, dust in sunlight, plant cycles, water/bowl shimmer, distant birds/insects, snow, and moving branch shadow;
- distribute/phase ambient loops so they do not all animate in sync;
- keep ambient motion quieter than Moss and normally outside attention/behavior semantics;
- add deterministic placed local lighting such as bedside/desk/window light where composition supports it;
- achieve strong cool-night vs warm-interior contrast using hard-edged pixel-native light treatment, never bloom or smooth gradients;
- make rain/mist affect whole-scene palette/light mood in addition to local window marks.

Success means a quiet Moss can sit in a world that still feels alive, atmospheric, and temporally specific.

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
