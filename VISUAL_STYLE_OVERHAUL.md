# Terrarium Visual Style Overhaul

This file is the implementation roadmap for bringing Terrarium's visible world into the target art territory described by the 2026-08-27 visual-art audit while preserving Terrarium's own identity, architecture, simulation, and product thesis.

`ART_DIRECTION.md` remains the visual law. This file defines the migration plan from the current procedural renderer to the richer authored visual ecology that law now requires.

## Target in one sentence

Terrarium should feel like a **hand-authored, late-16-bit life-RPG diorama built on a strict low-resolution grammar, emotionally enriched through saturated natural color, readable silhouettes, layered depth, environmental detail, selective low-frame animation, atmospheric lighting, slow environmental transformation, and visible history**.

The goal is not to copy another game's assets, characters, architecture, UI, exact palette, map structure, or subject matter. The transferable target is the system-level visual grammar.


## Source audit provenance

This plan distills the external research artifact **`2026-08-27--video-game-art-animation-world-audit.md`** supplied during the 2026-08-27 visual-gap review. The full audit is not currently checked into this repository. Its implementation-relevant conclusions are intentionally captured here and in `ART_DIRECTION.md` so ordinary development does not depend on a chat attachment.

If a future art-review session needs the audit's full evidence trail, examples, caveats, or source bibliography, provide that original `.md` as supplemental reference. It is not required to execute Iteration 8A–8F from repository authority.

Terrarium already differs on major structural axes: a single persistent domestic habitat rather than a multi-region farming world, a dog hero with different proportions rather than human overworld sprites, history-driven room transformation, and Terrarium-specific lighting/material/composition choices. Preserve those differences while applying the audit's system-level principles.

## Why this overhaul exists

Terrarium already satisfies many mechanical pixel-art constraints:

- 400×240 source art surface;
- exact 2× nearest-neighbor presentation at 800×480;
- smoothing disabled;
- finite deterministic palette states;
- clustered hard-edged drawing;
- low-frame action posing;
- persistent visual aftermath;
- authoritative spatial staging and occlusion;
- deterministic weather/events;
- no camera shake, random zoom, bloom, or renderer-owned behavior.

The limiting factor is no longer pixel compliance. The current reference renderer still authors most room art and Moss through procedural JavaScript rectangles and helper functions. That makes refinement possible, but it creates a ceiling on silhouette quality, material richness, asymmetry, sprite acting, depth, and long-term visual transformation.

The simulation is currently ahead of the art. The next work should let the visual system catch up before materially expanding behavior again.

## Non-negotiable product invariants

The overhaul must preserve all accepted Terrarium authority boundaries:

- canonical semantic/reference frame remains 800×480;
- authored art remains 400×240 and presents at exact 2× scale;
- canonical movement remains continuous semantic space, not tile movement;
- world engine owns behavior, targets, routes, object state, event state, time, history, habits, and environmental facts;
- renderer may stage and animate authoritative state but may not invent causes, preferences, navigation, history, or world events;
- canonical Moss and the live runtime are user-owned and must never be replaced by development fixtures;
- deterministic replay and current behavior/spatial/habit/situational contracts remain protected unless an iteration explicitly changes them;
- subjective charm is judged through actual visual review, not a synthetic beauty score.

## Core structural grammar

### 1. Art grid

Use **16×16 source pixels** as the primary static-world art/composition unit.

At the current 400×240 source surface this creates an exact **25×15 art grid**. At presentation size one art tile corresponds to 32×32 semantic/display pixels.

This is an **art and composition grammar**, not a simulation-navigation grid. Moss and movable props remain positionable at arbitrary authoritative coordinates.

### 2. Authored assets instead of procedural illustration

Move the source of truth for visible art out of hard-coded `rect(...)` compositions in `display/web/app.js` and into text-addressable, deterministic pixel assets.

Preferred source layout:

```text
display/art/
    palettes/
        materials.json
        lighting.json
        seasons.json
    tiles/
        walls.json
        floors.json
        rug.json
        structural.json
        foliage.json
    props/
        furniture.json
        clutter.json
        objects.json
    moss/
        idle.json
        walk.json
        inspect.json
        nudge.json
        pickup.json
        carry.json
        place.json
        loaf.json
        groom.json
        stretch.json
        react.json
        window-watch.json
        sleep.json
        wake.json
    environment/
        window-exterior.json
        rain.json
        leaves.json
        moths.json
        ambient-life.json
```

The exact format may evolve, but the source should remain:

- human-readable;
- diffable in Git;
- AI-editable;
- deterministic;
- palette-indexed or palette-addressable;
- easy to validate;
- cheap to precompile/cache into offscreen canvases or atlases;
- compatible with a future embedded renderer.

A packed atlas may be generated later. It should not become the only editable source of truth.

### 3. Declarative depth and occlusion

Replace special-case draw ordering with a scene-layer contract approximately equivalent to:

```text
BACK
  wall
  exterior/window
  base floor

STRUCTURE
  architecture
  furniture bodies

SURFACE
  rug
  path wear
  low props
  history marks

WORLD
  persistent objects
  ambient creatures/effects with physical location

ACTORS
  Moss
  carried object

FRONT
  blanket edge
  desk edge
  shelf lips
  foreground foliage

ALWAYS_FRONT
  rare foreground atmosphere
```

Within compatible dynamic layers, use foot/base Y ordering where it improves occupancy. Foreground occlusion should make the room feel spatially inhabited without hiding action contacts.

## Color direction

Terrarium's previous wording overemphasized muted/low-saturation cozy color. The new target is **earthy but frequently saturated**.

Preferred material behavior:

```text
material family
  deep chromatic edge
  cool/chromatic shadow
  base local color
  warm/lit midtone
  selective highlight
```

Use compatible families rather than one tiny global master palette.

Direction:

- richer moss and forest greens;
- reddish walnut and warm timber browns;
- clearer blue and blue-green environmental shadows;
- brighter amber/gold focal accents;
- warm cream cloth/paper highlights;
- higher-chroma flowers, leaves, papers, toys, and small focal props when compositionally useful;
- darks should usually remain chromatic rather than dead black;
- highlights may shift warmer while shadows shift cooler.

Avoid neon color, washed-out pastel sameness, giant near-identical ramps, glossy gradients, and universal black outlines.

## Room composition and zone identity

Terrarium remains one persistent habitat. Do not turn it into a multi-map town or farming game.

Translate the target world's regional-identity principle into distinct material and emotional zones inside the existing room:

### Window / outside world

Identity: **nature, weather, distance, change**.

- richer exterior foliage and sky states;
- season/time/weather variation;
- readable sill, curtain, frame, glass, leaves/branches;
- birds, rain, snow, moths, leaf contact, moving sunlight, and other bounded exterior/ambient life;
- cool exterior colors can contrast with interior warmth.

### Sleeping nook

Identity: **softness, safety, domestic warmth, accumulated habit**.

- visibly layered bedding;
- compression and creases from actual history;
- soft cloth palette family;
- local warm light candidate;
- foreground blanket overlap for depth.

### Rug / open living space

Identity: **quiet movement field and visual rest**.

- keep it broad and readable;
- do not fill every tile with texture;
- use subtle wear and controlled motif variation;
- preserve enough negative space for Moss and object actions to read.

### Collection shelf

Identity: **memory, arrangement, accumulation**.

- strong silhouette and top/front/recessed planes;
- persistent items should read as a changing composition rather than identical tokens;
- foreground lips support real occlusion;
- authored object-state variants should make collections tell history.

### Activity corner

Identity: **curiosity, work, clutter, experimentation**.

- desk, papers, plant, tools/clutter, local material accents;
- higher controlled detail density than the open rug;
- persistent marks should make repeated use visible;
- local lamp is a strong candidate for night lighting.

## Moss sprite overhaul

Preserve the accepted semantic action vocabulary and timing. Replace procedurally assembled body/head/leg rectangles with true authored sprite frames.

Moss does **not** need to use another game's human 16×32 body scale. Moss is the single hero of a 400×240 habitat and can keep approximately the accepted 40–46×30–38 px active silhouette if visual tests support it.

Author a compact frame vocabulary for:

- idle / restrained breathing;
- four-frame locomotion;
- inspect anticipation/contact/hold;
- nudge contact/recovery;
- pickup contact/transfer;
- carry;
- place lower/contact/release/settle;
- loaf;
- groom;
- stretch;
- react/orient;
- window watch;
- sleep transition;
- curled sleep;
- wake/unfold.

Priorities:

- readable outer silhouette;
- floppy asymmetrical ears;
- clear muzzle/head orientation;
- planted feet;
- tail shape as an acting cue, not constant noise;
- visible compression/extension for posture;
- strong contact with objects/furniture;
- low frame count with deliberate holds and timing;
- no skeletal smoothing or random fidget layer.

## Environmental animation

Situational events remain authoritative and selective. Add a second category: **persistent non-commanding ambient life**.

Examples:

- subtle foliage movement outside;
- curtain drift;
- water/rain runoff on the pane;
- occasional leaf drift;
- dust visible in a sunlight patch;
- plant-leaf cycle;
- bowl/water shimmer where appropriate;
- distant bird/insect motion;
- snow;
- moving branch shadow;
- small local lamp/fire-like animation if a fitting fixture exists.

Ambient loops must be spatially distributed, phase-varied, low-amplitude, and quieter than Moss. They do not automatically create attention events or behavior decisions.

## Lighting and weather

The existing dawn/day/dusk/night palette states are a base, not the finished system.

Add deterministic local light sources such as:

- bedside lamp;
- desk lamp;
- moon/window light;
- occasional exterior/environmental light when grounded in canonical state.

Render local light with stepped/hard-edged pixel masks or palette variants, not smooth gradients or bloom.

Night target:

> **cool blue/indigo ambient room + localized warm amber domestic light.**

Weather should alter the whole scene's color relationship in addition to visible window marks. A rainy afternoon should feel rainy from the room palette and light balance even when the viewer ignores the rain streaks.

## Seasons and slow environmental transformation

Add seasons only after the core asset/layer/room/Moss pipeline is stable.

Terrarium's accelerated world day is approximately 72 real minutes. Therefore a direct 28-world-day season would pass far too quickly. Seasonal cadence must be a separate, much slower canonical timescale while remaining deterministic and replayable.

Candidate visual identity:

- **Spring:** fresh greens, blossoms, clear blues, small bright accents;
- **Summer:** deeper/full greens, strongest sunlight, insects, fuller foliage;
- **Autumn:** orange/red/rust foliage, leaf debris, warmer wood harmony;
- **Winter:** pale/snow exterior, sparse foliage, blue-violet shadows, strongest cold-outside/warm-inside contrast.

Stable room landmarks and geometry should remain recognizable across all seasons.

## Persistent history as art

Terrarium's strongest unique advantage is that visible changes can be grounded in actual stored history rather than decorative fakery.

Increase the visual payoff of history over time:

- bedding compression/rumpling grows and changes;
- favorite paths wear subtly;
- favorite resting places develop small supported traces;
- shelf composition persists and evolves;
- activity papers/marks accumulate and rearrange;
- window marks appear, change, and fade;
- plants can slowly grow/change if canonical state supports it;
- objects migrate toward habitual arrangements;
- rare situations may leave small persistent traces;
- heavily used and lightly used areas should gradually look different.

The renderer may visualize only authoritative counters/state/history. It must not invent a backstory merely because a mark would look attractive.

## Object Identity integration

The previously planned Object Identity / Stateful Affordances work remains valuable, but it should follow the renderer foundation and room/Moss art passes.

When implemented, behavior state and visual state should evolve together. Examples:

- thread: neat coil → loose → dragged → tangled;
- leaf: fresh → displaced → crumpled/dry;
- stone/ball: stable → rolled orientation → partly hidden;
- cloth/paper: folded → rumpled → dragged → piled/nested;
- container: empty/open/occupied/closed as supported by actual mechanics.

Object class should alter both the available affordances and the visible consequences.

## Visual review harness

Create project-local visual review tooling rather than a synthetic aesthetic oracle.

Target tool: `tools/capture_art_direction_matrix.py` (name may vary if implementation evidence suggests a better interface).

It should capture deterministic real-browser states spanning representative combinations of:

- dawn/day/dusk/night;
- clear/rain/mist and later snow;
- fresh vs lived-in room;
- key Moss poses/actions;
- representative object states;
- selected events;
- later, all seasons.

Desired outputs:

- lossless screenshots;
- contact sheets / side-by-side matrices;
- short temporal clips or keyframe sequences where useful;
- machine-readable metadata tying every image to canonical fixture state and renderer/source hash.

Automation should judge objective contracts only: exact scale, smoothing state, deterministic repeat, declared grid/layer contract, allowed palette behavior where mechanically specified, occlusion correctness, and known temporal defect classes.

Human/vision inspection remains authority for composition, charm, material coherence, silhouette quality, detail density, color balance, and whether the target art territory is actually reached.

## Ordered implementation plan

### Iteration 8A — Visual Grammar and Asset Pipeline

**Status: ACCEPTED** — see `history/2026-08-27-pixel-art-overhaul-iteration8a.md` and snapshot `20260828T020631095429Z-pixel-art-overhaul-iteration8a`.

**Purpose:** remove the procedural-art ceiling before adding more visual complexity.

Deliver:

- 16×16 static-world art grid contract;
- text-addressable palette-indexed pixel asset format;
- source directories and validation;
- asset compilation/caching into the Canvas renderer;
- palette-bank/material system;
- declarative scene-layer model;
- generalized foreground occlusion / Y-ordering where appropriate;
- deterministic visual fixture support;
- initial art-direction capture matrix;
- migration of enough representative current art to prove the pipeline end-to-end.

Do **not** expand Moss intelligence, object behavior, seasons, or world-event semantics in this iteration.

Success means the renderer can express the desired visual language cleanly without hard-coding every finished sprite/tile into `app.js`.

### Iteration 8B — Room Recomposition

**Status: ACCEPTED** — see `history/2026-08-27-pixel-art-overhaul-iteration8b.md` and snapshot `20260828T023312695923Z-pixel-art-overhaul-iteration8b`.

**Purpose:** make a still frame inhabit the target visual territory.

Deliver:

- redraw/recompose the full habitat using authored assets;
- richer saturated natural palette behavior;
- stronger furniture/zone silhouettes;
- clearer material families;
- controlled organic asymmetry;
- richer foliage/exterior through the window;
- denser authored detail around focal clusters;
- preserved quiet open rug/navigation field;
- improved foreground framing and spatial depth;
- no loss of authoritative persistent-history marks.

Success means the room reads as a richly authored late-16-bit life-RPG interior even with Moss hidden.

### Iteration 8C — Moss Sprite Overhaul

**Status: ACCEPTED.**

**Purpose:** give the hero the same authored visual maturity as the room.

Deliver true authored sprite frames for the existing accepted action semantics, with silhouette/charm/contact acting as the primary criteria.

Success means Moss looks like a specific appealing inhabitant of the room rather than a procedural approximation of a dog.

Accepted 8C uses 46 palette-addressed Moss assets, four authored walk frames, discrete contact/quiet/sleep/wake poses, and renderer-only canonical frame selection. Procedural finished-body assembly and constant idle/sleep bobbing are retired. Accepted evidence is `history/2026-08-27-pixel-art-overhaul-iteration8c.md`; snapshot `20260828T030258821895Z-pixel-art-overhaul-iteration8c`.

### Iteration 8D — Object Identity and Stateful Affordances

**Status: ACCEPTED.**

The six persistent objects now have canonical archetypes and interaction state. Rolling, soft-nesting, delicate, and keepsake identities expose different affordance subsets; stateful chains alter later possibilities; and 13 authored object-state variants make those consequences visible. Object identity remains subordinate to the existing habit/exploration architecture rather than becoming a planner or inventory system.

Accepted evidence: `history/2026-08-28-pixel-art-overhaul-iteration8d.md`; snapshot `20260828T112207258140Z-pixel-art-overhaul-iteration8d`; semantic frame `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`.

Success criterion met: object identity now changes both what Moss can do and what the viewer can see afterward.

### Iteration 8E — Atmospheric World

**Status: NEXT.**

Add persistent non-commanding environmental motion, richer window life, placed local lighting, and stronger whole-scene weather mood.

Success means the room remains visibly alive while Moss is still, without becoming busy or demanding.

### Iteration 8F — Seasonal Terrarium

Add a slow canonical seasonal timescale plus coordinated palette, foliage, lighting, weather/particle, exterior, and selected interior changes.

Success means a familiar room changes enough over long real-world time that season itself becomes meaningful visual content.

### Iteration 9 — Emergent Situations and Consequence Memory

Return to the planned systems milestone after the visual/state space is richer. Let event state, object state, arrangements, habits, and accumulated consequences create later opportunities without scripted quests or a generic planner.

## Convergence passes

After the structural overhaul, schedule explicit redraw/taste-convergence passes. They are allowed to remove or simplify work rather than only add features.

Potential passes:

- silhouette pass;
- color/value pass;
- material-language pass;
- room density / negative-space pass;
- Moss charm/acting pass;
- lighting pass;
- ambient animation pass;
- clutter-reduction pass;
- seasonal consistency pass;
- long-duration observation pass.

A coherent visual system is expected to emerge through repeated comparison and redraw, not from treating the first asset pipeline as finished art.

## Explicit non-goals

Do not:

- turn Terrarium into a farming game;
- introduce NPCs merely to resemble another life RPG;
- copy recognizable buildings, crops, furniture, UI, characters, or sprite sheets;
- copy an exact external palette;
- replace the single persistent habitat with multiple local maps;
- make 16×16 tiles authoritative movement cells;
- move behavioral/world authority into JavaScript presentation code;
- add smooth skeletal animation;
- add constant Moss fidgeting;
- use generic generated pixel-art assets without normalizing them into Terrarium's visual grammar;
- add bloom, blur, soft-focus post effects, camera shake, or random zoom;
- fill every quiet surface with decoration.

## Final visual acceptance target

**Without Moss visible:** the habitat should read as a deliberate, richly authored late-16-bit life-RPG interior with crisp enlarged pixels, saturated natural materials, strong silhouettes, layered depth, asymmetrical handcrafted placement, controlled detail density, clear visual rest, and evidence that time passes there.

**With Moss visible:** the same scene should additionally feel like this particular room belongs to this particular dog—his habits, possessions, repeated routes, favorite places, interactions, and history should gradually alter the image.

That combination—authored visual grammar plus persistent personal history—is Terrarium's own identity.
