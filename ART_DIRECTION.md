# Terrarium Pixel-Art Direction

This file is the visual authority for Terrarium. Human/vision inspection of the real renderer governs charm, coherence, composition, and appeal. Automated evaluators protect mechanical correctness; there is no synthetic beauty score.

`VISUAL_STYLE_OVERHAUL.md` defines the ordered migration from the current procedural renderer to this target. This file defines the law the resulting art should obey.

## Rendering contract

- Author art on a **400×240 internal Canvas surface**.
- Present at the fixed external/reference **800×480** size using exact **2× integer nearest-neighbor scaling**.
- Keep both internal drawing and final scaling smoothing disabled.
- Snap semantic 800-space presentation coordinates to the 400×240 art grid at the renderer boundary; canonical `TerrariumFrame` coordinates remain hardware-neutral and authoritative.
- Never draw high-resolution 800×480 art and pixelate it afterward.
- Avoid subpixel antialias-dependent drawing, gradients, blur, bloom, soft-focus post-processing, and glossy effects.
- Use **16×16 source pixels** as the primary static-world art/composition unit. At 400×240 this yields an exact 25×15 art grid. This is an art grammar, not a navigation grid.

## Target aesthetic

A hand-authored late-16-bit life-RPG diorama: warm, colorful, readable, materially grounded, nature-connected, slightly whimsical, and rich enough that the habitat itself remains interesting when Moss is still.

The defining target is not merely “pixel art” or “cozy.” It is the interaction of:

- strict small-grid construction;
- strong readable silhouettes;
- saturated natural color relationships;
- clustered shading and selective chromatic outlines;
- pragmatic overhead/three-quarter illustration;
- layered depth and foreground occlusion;
- low-frame pose-driven character acting;
- non-commanding environmental animation;
- meaningful day/weather/season lighting shifts;
- controlled detail density with real negative space;
- visual state that changes because time, habit, and history happened.

The room should look authored rather than procedurally assembled. Individual assets should feel like members of one visual ecology.

## Authored asset law

Finished sprites, tiles, props, and recurring environmental art should live in deterministic text-addressable pixel assets (or an evidence-backed equivalent source format) rather than requiring `display/web/app.js` to be their primary illustration tool.

Preferred properties:

- human-readable and Git-diffable;
- palette-indexed or palette-addressable;
- dimension-validated;
- deterministic;
- cacheable/precompilable;
- easy for human and AI editing;
- suitable for later packing into an atlas or embedded-display representation.

Renderer code should increasingly describe **composition, state selection, layering, timing, and presentation**, while art files describe the actual pixel clusters.

## Color and palette behavior

Terrarium is **earthy but not desaturated**. Natural materials may be quite colorful.

Core families remain useful but their behavior is richer:

- **moss / forest green** — rug and foliage, ranging from deep forest/chromatic shadow through strong natural greens;
- **walnut / reddish timber** — furniture, trim, outlines, floor depth;
- **golden amber** — warm accents, leaves, lamplight, daylight highlights;
- **clear / dusty blue family** — blanket, sky/weather, cool environmental shadow, winter/night accents;
- **cream** — cloth, paper, selective highlights;
- **Moss brown** — warm medium brown body with dark chromatic brown shadow/ears and restrained warm highlights.

Prefer **palette behavior** to one tiny global master palette. A material may use roughly:

1. deep chromatic edge/contact;
2. cooler/chromatic shadow;
3. base local color;
4. warmer/lit midtone;
5. selective highlight where warranted.

Use 2–5 meaningful shades where the object needs them; do not add shades merely to smooth ramps. Highlights should often shift warm and shadows may shift cool. Focal props can receive stronger hue/value contrast than background material.

Avoid washed-out pastel sameness, dead-black shadow dependence, neon saturation, giant near-identical ramps, or universal pure-black outlines.

## Pixel-cluster and material rules

- Build forms from intentional rectangles/stair-steps and connected clusters, not smooth analytic curves.
- Silhouette carries identity before micro-detail.
- Prefer coherent color clusters over scattered single-pixel noise.
- Use selective dark/chromatic outlines where they improve separation; break or lighten outlines where adjacent values already explain the form.
- Texture communicates material: wood grain, cloth stitching/creases, leaf clumps, flowers, floor scuffs, paper marks, bedding compression, stone facets, glass/wet traces.
- Organize density hierarchically: quiet planes → medium-frequency structural edges → high-frequency focal accents.
- Break tile repetition with deterministic authored asymmetry and stable variation; never use runtime `Math.random`.
- Keep noisy texture away from Moss's face, action contacts, and important silhouettes.
- One-pixel highlights are accents, not a blanket sparkle layer.

## Perspective and scale

Use a pragmatic overhead/three-quarter illustrated view. Readability outranks physically exact perspective.

Ground/floor can read mostly overhead while furniture exposes whatever top/front/side faces make it instantly understandable. Depth comes from overlap, vertical ordering, value separation, stepped planes, contact shadows, and foreground occlusion.

Useful source-art scale conventions at 400×240:

- static-world composition unit: **16×16 px**;
- Moss hero sprite: approximately **40–46 px wide × 30–38 px tall** including ears/tail in active poses, unless visual evidence supports a bounded change;
- movable props: approximately **8–12 px** major dimension, with category-readable exaggeration allowed;
- furniture edges: typically **2–6 px** thick depending on importance;
- contact shadows: usually **1–3 px** tall and narrower than the subject.

Do not force Moss into a human 16×32 sprite convention merely because the static world uses 16×16 art tiles.

The large rug/open center remains a composition anchor, movement field, and negative-space buffer around Moss.

## Composition and density

The room should alternate **density and rest** rather than filling every cell.

- landmarks/furniture must read before decoration;
- object silhouettes should remain distinct at a glance;
- open rug/floor gives Moss room to act and prevents focal clusters from merging;
- denser detail belongs around window foliage, shelf collections, bedding, desk/activity materials, and selected edges;
- organic asymmetry should soften the underlying grid;
- repeated motifs should vary through authored clusters rather than random pixel noise.

A still frame should be visually interesting, but Moss must remain legible immediately when present.

## Room identity

Preserve the persistent Terrarium habitat rather than replacing it with a decorative mockup or multi-map world.

- **Window / weather:** nature, outside distance, weather, seasonal change, foliage, curtain/sill/glass depth.
- **Sleeping nook:** softness, safety, domestic warmth, bedding history, foreground blanket overlap.
- **Rug / open space:** calm visual rest, navigation/acting field, subtle wear.
- **Collection shelf:** memory, accumulation, persistent arrangements, top/front/recessed planes, foreground lips.
- **Activity corner:** curiosity, papers/tools/plant/clutter, repeated-use marks, stronger controlled detail.
- **Bowls and persistent objects:** readable category silhouettes with authored state-specific visual variants.

Persistent history remains visible in pixel language: worn routes, object scuffs, sleep compression/creases, window smudges/wet traces, activity papers/marks, object arrangements, and future supported causal aftermath. These marks must derive from canonical history/state; renderer presentation may not invent history.

## Moss sprite language

Moss is a **small expressive brown floppy-eared dog** with a distinct hand-authored silhouette:

- compact body;
- slightly oversized head;
- floppy asymmetrical ears;
- short planted legs;
- readable muzzle/head direction;
- readable tail used sparingly as an acting cue;
- minimal face with dark eye/nose pixels;
- strong side/three-quarter gameplay silhouette.

The default sprite has **no glasses** and does not depend on accessories for identity.

Prefer authored sprite frames over procedural body-part deformation. Meaningful action uses a small discrete pose vocabulary with deliberate timing.

Required hero-pose vocabulary:

- idle/rest: compact planted stance; stillness is valid and no random breathing/ear/tail fidget loop is required;
- locomotion: four readable contact/weight-shift keyframes, mirrored as appropriate, minimal vertical bob;
- inspect/contact: target-facing anticipation, gaze/head shift, bounded forepaw/lean contact, hold/recovery;
- nudge: visible paw/contact before authoritative displacement, then regard/recovery;
- pickup: contact first, then transfer into a stable chest/paw hold;
- carry: rigid object attachment and steadier posture;
- place: stop → lower/contact → release → settle → retract;
- loaf: distinct relaxed supported silhouette;
- groom: compact contextual pose, not constant fidget;
- stretch: readable extension/compression with planted contact;
- react/orient: small attention shift, not alarm theater;
- sleep: supported transition into a curled bed pose with bedding overlap;
- wake: deliberate unfold/stand transition;
- window watch: planted sill-facing observation with quiet posture.

Favor pose choice, silhouette, contact, and frame timing over high frame counts or smooth tweening.

Accepted Iteration 8C implementation:

- 46 deterministic Moss assets live under `display/art/moss/`;
- `display/web/app.js` selects/stages those assets from canonical state rather than constructing the finished dog from body-part rectangles;
- four locomotion sprites carry the visible weight shift while semantic movement stays continuous;
- exact target-dependent forepaw reach is the only bounded procedural Moss detail retained for canonical contact alignment;
- whole-sprite idle/sleep bobbing is removed; final quiet/sleep holds may remain completely still.

Accepted Iteration 8D object-state implementation:

- object art now follows canonical `terrarium.object-affordances.v1` archetype/state rather than a renderer-only kind recipe;
- rolling objects visibly distinguish `settled` and `rolled`; soft thread distinguishes `loose`, `rumpled`, and `nested`; keepsakes distinguish handled/displayed; the leaf distinguishes fresh/handled;
- state variants remain presentation only: the world decides archetype, interaction state, available affordances, transitions, zone and position;
- soft-object nest presentation is only valid where canonical affordances permit it (`open_space` / `sleeping_nook`); do not decorate a shelf/desk/window object as a nest merely for composition;
- object-specific arrangement should read as a tendency shaped by identity + learned habit, not as fixed prop placement or scripted set dressing;
- carried attachment and transition interpolation may stage canonical state, but must not create a visual state transition before the authoritative object event supports it.

## Depth and occlusion

Use a declarative depth system rather than a growing set of draw-last exceptions.

Target layer grammar:

1. **BACK** — wall, window exterior, base floor;
2. **STRUCTURE** — architecture and main furniture bodies;
3. **SURFACE** — rug, wear/history marks, low props;
4. **WORLD** — persistent objects and spatial ambient entities;
5. **ACTORS** — Moss and carried object;
6. **FRONT** — blanket/desk/shelf lips, foreground foliage and overhangs;
7. **ALWAYS_FRONT** — rare foreground atmosphere only when justified.

Use foot/base Y-ordering within compatible dynamic layers where it improves occupancy. Occlusion should clarify where Moss is standing, sitting, sleeping, or passing behind something; it should not obscure action contacts unnecessarily.

## Environmental animation

Situational events are not the only source of environmental motion. The finished room should support quiet persistent **ambient life** that normally carries no behavior command.

Candidate ambient motion:

- exterior foliage;
- curtain drift;
- rain runoff/condensation;
- occasional leaf drift;
- dust in sunlight;
- plant cycles;
- subtle water/bowl shimmer;
- distant bird/insect motion;
- snow;
- branch-shadow motion;
- localized lamp/fire-like animation where an actual fixture exists.

Ambient motion must be deterministic, spatially distributed, phase-varied, low-amplitude, and subordinate to Moss. Do not animate every instance in lockstep. Do not convert every atmospheric motion into an attention event.

Accepted Iteration 8E atmospheric implementation:

- ambient presentation derives from canonical `world_minutes`, lighting, weather, and event/frame state; no ambient behavior authority or persistent animation state was added;
- three authored exterior foliage layers use independent held-step periods, with a separate restrained curtain cycle rather than one shared sine wave;
- rain traces use multiple deterministic periods and sparse runoff; mist uses discrete drift; clear daylight may show localized motes, branch-shadow movement, and infrequent water shimmer;
- night uses finite warm palette variants and hard-edged floor/highlight accents around actual nook/desk light sources rather than gradients, bloom, alpha glow, or blur;
- rain and mist modify whole-scene palette treatment as well as the window;
- ambient effects stay below actor/foreground priority and must remain quieter than Moss and active situational events;
- looping distant creatures, generic leaf particle fields, snow without seasonal authority, and full-room sparkle remain unaccepted until a later evidence-backed need exists.

## Lighting, time, and weather

Dawn/day/dusk/night remain finite authoritative environmental states, but the visual treatment may become substantially richer.

- local object color should be clearest in daylight;
- night should cool the overall room into blue/indigo families;
- placed warm light sources may create localized amber/yellow pools using hard-edged pixel-native masks or palette variants;
- windows, lamps, and other lights should become more compositionally important after dark;
- no smooth bloom, blur, or airbrushed light gradients.

The key nighttime emotional strategy is **cool environment + warm shelter**.

Weather is a whole-scene modifier, not only a window overlay. Rain/mist may alter palette/value balance and make local warm light more valuable while remaining canonical/deterministic. Visible streaks, mist, wet traces, or snow remain sparse and pixel-native.

## Accepted Iteration 8F seasonal visual law

Seasons repaint a familiar place without destroying its identity. Seasonal authority is canonical `terrarium.seasons.v1`, never renderer uptime or an assumed default. The accepted cadence is **21 real days per season** with discrete **early / full / late** 7-day stages, producing an **84-day full cycle**. Existing worlds start at spring/early from their first post-upgrade observation with `migration_origin=neutral-existing-world`; do not fabricate historical seasonal progression.

- structural room landmarks, furniture geometry, Moss identity, object positions/state, and stored history remain stable unless another canonical system changes them;
- **spring** uses fresh exterior greens and sparse blossom accents;
- **summer** uses fuller/deeper exterior greens and denser canopy;
- **autumn** uses rust/ochre foliage and visibly thins from early → full → late;
- **winter** replaces dense foliage with a sparse pale exterior and authored branches, strengthening the existing cool-outside/warm-shelter strategy at night;
- seasonal color is a finite palette/material treatment, not a smooth full-screen filter;
- canonical weather remains independent and is applied after season; local warm light remains later still;
- absent canonical season must render the accepted neutral room rather than silently assuming spring;
- season itself carries no behavior command in Iteration 8F and must not make Moss act, change weather/event occurrence, or create hidden renderer memory;
- snow, holidays, random falling-leaf fields, smooth seasonal crossfades, gradients, bloom, blur, and fog masks remain outside the accepted 8F grammar.

The long-horizon visual question is now: **after enough real time passes, does the same room clearly belong to a different season while still reading instantly as Moss's persistent home?**

## Accepted Iteration 9 causal presentation law

Consequence memory is simulation authority, not visual memory. A delayed consequence may change *why* Moss pauses, walks, inspects, rests, loafs, or watches the window, but the renderer must not invent the cause or remember it privately. Prefer existing authored acting and persistent object/world state over explicit UI. If a future causal chain is unreadable, add only a bounded canonical visual cue justified by UAT. Quest markers, thought bubbles, floating labels, and renderer-side narrative state are not part of the accepted grammar.

## Motion rules

Canonical behavior, target ownership, route geometry, event occurrence, and pacing remain outside renderer authority.

- Heartbeat continuation must not restart animation clocks.
- Motion may be deliberately grid-quantized at the 400×240 art boundary, but semantic/presentation interpolation remains deterministic and continuous before quantization.
- Never add random jitter to fake liveliness.
- Anticipation, contact, hold, settle, and recovery should read as distinct key-pose phases.
- Carried objects remain rigidly attached after transfer.
- Environmental animation is slower/quieter than character acting.
- Whole-scene motion is prohibited unless a future explicit art decision establishes a bounded use; camera shake/random zoom remain prohibited.

`temporal-render-auditor-r1` and `grid-quantized-temporal-render-auditor-r1` remain objective rejection gates. Neither judges artistic quality.

## Visual review and acceptance

Evaluate the real renderer across representative combinations of time, weather, history, action pose, object state, events, and later seasons. Prefer deterministic screenshots/contact sheets plus temporal samples over judging isolated sprite files.

A checkpoint should be rejected if the actual 800×480 output feels:

- filtered or smooth/vector-like;
- washed out or uniformly muted;
- neon/glossy;
- flat despite available depth;
- mechanically tiled without controlled asymmetry;
- dependent on micro-detail instead of silhouettes;
- noisy everywhere with no visual rest;
- procedurally generic rather than authored;
- temporally frantic;
- visually disconnected from canonical history;
- or if Moss ceases to be the focal inhabitant.

Later convergence passes are expected to redraw, remove, recolor, or simplify existing work. Cohesion comes from repeated taste convergence, not from adding assets forever.

## Accepted Iteration 2 acting/detail refinement

Pixel-Art Overhaul — Iteration 2 established a stricter authored-acting rule: meaningful actions use a small discrete pose vocabulary rather than continuous body deformation. Locomotion uses four authored contact/weight-shift keyframes with planted-foot readability and restrained ear/tail response. Inspect, pickup, carry, place, window watching, rest, sleep, and wake each have action-specific staging; renderer subposes may interpret canonical intent but never choose targets or mutate world state.

Environmental craft follows the same hierarchy. Prefer recognizable top/front/recessed planes, shelf/sill/blanket lips, furniture supports, sparse material clusters, and hard contact shadows over broad primitive rectangles or surface noise. Persistent wear/aftermath may become visually richer only when authoritative frame state supports it. Human inspection remains the authority for silhouette, charm, composition, and material coherence; temporal auditors remain rejection gates for objective motion defects only.

## Accepted Iteration 3 spatial/depth conventions

Pixel-Art Overhaul — Iteration 3 makes physical staging part of the visual law. Illustrated furniture footprints and authoritative navigation geometry must agree: Moss stands on readable floor/contact space, never inside a cabinet/desk/wall just because a semantic zone points there. Window, shelf, activity corner, bowls/props, and the sleeping nook expose believable open-side approach positions.

Routes may contain a small number of authored intermediate waypoints. Turns should happen at legible room corners without facing chatter. The renderer follows the authoritative route and may not shortcut through furniture. Sleep may overlap bedding only at the explicit supported bed anchor; wake must visibly leave the support through the bed gate before ordinary behavior resumes.

Depth remains pixel-native and authored. Use low perch/tray/top/front planes and foreground lips where needed to explain usable surfaces. Occlusion should follow physical position, not a global draw-last rule. Carried-object attachment must remain visually continuous when Moss changes facing at a route corner.
## Accepted Iteration 4 behavioral acting conventions

Pixel-Art Overhaul — Iteration 4 makes **behavioral continuity part of acting readability**. The renderer still has no behavioral authority, but authored poses should have enough canonical dwell to read as a session rather than a flicker. Arrival normally earns a planted settle before another trip. Window watching is a viewing bout. Inspect→pickup→carry→place may read as one object-centered chain. Placement includes a brief regard/recovery, and waking includes a supported unfold/recovery before ordinary travel.

Stillness is valid acting. Do not add secondary motion, random ear/tail noise, or extra walking merely to keep the screen busy. A quiet planted Moss who has a readable reason to remain where he is is preferable to visually diverse but purposeless motion. The strongest acting question is now: **does this pose look like a continuation of what Moss just chose to do?**

Favorite spots are authored physical affordances, not renderer inventions. Any future visual differentiation of a favorite spot must be grounded in canonical state/history rather than hidden presentation memory.

## Accepted Iteration 5 long-horizon habit conventions

Pixel-Art Overhaul — Iteration 5 makes **repetition across days part of character readability** without giving the renderer any memory or behavioral authority. A viewer should be able to infer a favorite only from Moss repeatedly choosing a place, object, or context over time. Do not add labels, badges, meters, glow, UI callouts, or renderer-only decoration that declares a preference.

Habits must remain visually alive rather than choreographed. Familiar places may recur, favorite objects may receive more attention, and time-of-day tendencies may become recognizable, but individual days still need variation and environmental responsiveness. The acting question expands from “does this pose continue the last action?” to **“over many visits, does this still look like the same creature making characteristic choices?”**


## Accepted Iteration 6 affordance acting conventions

Pixel-Art Overhaul — Iteration 6 makes **consequence part of action readability**. A new pose is not enough by itself: object play, arrangement, comfort, and environmental reaction should visibly belong to a short causal activity with a reason to begin, a readable middle, an authoritative consequence where applicable, and a calm recovery.

Nudge must read as approach/contact **before** displacement, followed by a brief regard of the changed object position. Carry/place should communicate a chosen arrangement rather than generic shuffling. Loaf, groom, and stretch are distinct quiet silhouettes and should not be exaggerated into constant fidgeting. Environmental `react` is an attention shift that may lead into an existing window-watch session; it must remain quieter than the weather itself and must not become alarm animation.

Habits may become visible through where these affordances recur: favorite zones can attract more loafing or arrangements and favored objects may participate somewhat more often. The renderer still never declares a favorite with UI, glow, labels, or hidden memory. Persistent arrangements and object displacement are canonical world history; the renderer only makes their consequences legible.


## Accepted Iteration 7 situational-event acting conventions

Pixel-Art Overhaul — Iteration 7 makes **external cause and selective attention part of visual readability**. Environmental events are not full-scene effects and they do not automatically make Moss perform. The renderer depicts canonical event state quietly enough that ignoring an event remains visually plausible.

Event presentation rules:

- moving sunlight is a hard-edged finite-palette patch on valid floor/rug space, never a smooth alpha spotlight or bloom;
- bird, leaf contact, rain escalation, and thunder stay localized to the window/pane and must not shake, zoom, flash, or recolor the whole room;
- a night moth is tiny, slow, integer-grid motion near its authoritative source and must not become a particle system;
- event motion is quieter than Moss acting and may not use `Math.random` or hidden renderer-only lifecycle state;
- the event's semantic/source position may differ from Moss's physical engagement stance; renderer staging must preserve that distinction rather than moving canonical navigation into presentation code;
- a non-reaction is valid presentation: the event may remain visible while Moss continues an unrelated committed activity;
- `react`, `look_outside`, and `loaf` should read differently when their canonical cause differs, but do not create gratuitous pose enums when gaze, target, context, and event depiction already communicate the cause.

The visual question is now: **does something seem to have happened in the room, and does Moss's degree of attention to it feel intentional rather than compulsory?** Moss remains the focal character even when the world initiates the moment.


## Accepted Iteration 8A authored-art foundation

Pixel-Art Overhaul — Iteration 8A makes the authored-art law executable. `display/art/manifest.json` now pins the exact 400×240 surface, 16×16 static composition unit, and 25×15 art grid while leaving canonical movement and `terrarium.spatial.v1` continuous. Palette-addressed `terrarium.pixel-asset.v1` sources hold recurring pixel clusters; the browser validates them, compiles them once into smoothing-disabled offscreen canvases, and caches by asset/palette rather than interpreting source text every frame.

The renderer now exposes the declarative `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT / ALWAYS_FRONT` scene grammar with stable Y/base ordering inside compatible layers. This is presentation ordering only; spatial/world authority remains canonical. Representative authored room, prop, Moss, tile, and environmental assets intentionally coexist with legacy procedural drawing until Iterations 8B and 8C migrate the remainder.

Visual-review evidence is now expected to pin both the renderer hash and authored-art tree hash. `tools/capture_art_direction_matrix.py` is the project-local deterministic review entry point. Automated checks may reject schema, dimensions, grid, scale, smoothing, determinism, temporal continuity, or renderer errors; they still may not manufacture a numerical charm/beauty score.


## Accepted Iteration 8B room-composition conventions

Pixel-Art Overhaul — Iteration 8B makes **the habitat itself authored art rather than a procedural backdrop**. Major static visual masses now belong in `display/art/` and should be palette-addressed, deterministic, diffable assets. Room-specific JavaScript rectangles remain appropriate for canonical dynamic overlays, interpolation, event effects, history marks, and other state-dependent presentation; they are no longer the preferred source of truth for finished architecture, furniture, rug, exterior, or foreground lips.

Room composition should preserve distinct zone identities without breaking the single-habitat product: the window is the cool nature/weather/distance cluster; the sleeping nook is warm, layered and soft; the collection shelf is a strong memory/accumulation silhouette; the activity corner may carry the highest controlled detail density; and the rug/open movement field remains deliberate visual rest. Richness belongs primarily around edges, furniture, materials and focal clusters—not uniformly across every floor tile.

The accepted palette direction is **earthy but materially richer and more saturated**. Prefer chromatic darks, reddish/warm timber, strong natural greens, clearer blue/blue-green exterior values, separated cloth ramps, warm cream highlights, and selective amber/terracotta/brass accents. Avoid returning to universal muted beige/brown, but also avoid neon, glossy ramps, dead-black outlining, gradients, bloom, or color noise without material purpose.

Controlled asymmetry is now part of the room language. Curtains, foliage, bedding, papers, small objects, and material clusters may break bilateral/grid repetition, but the large silhouettes and authoritative usable spaces must stay readable. The 16×16 art grid remains a composition grammar only; do not quantize Moss, objects, routes, event sources, or interaction anchors to tiles.

Depth should follow the accepted scene contract in the production path, not merely in manifest metadata: `BACK` for shell/exterior, `STRUCTURE` for architecture/furniture, `SURFACE` for rug/floor/history, `WORLD` for located objects/effects, `ACTORS` for Moss, and `FRONT` for genuine occluding lips/overhangs. Foreground pieces must explain spatial occupancy without hiding action contacts arbitrarily.

Persistent wear, bedding compression, activity clutter, window marks, object arrangements, and situational effects remain canonical-state visualizations. Do not bake fictional history into static assets merely because it improves a screenshot. The accepted 8B room provides a richer stage; the world engine still decides what has actually happened there.
