# Terrarium Pixel-Art Direction

This file is the visual authority for Terrarium. Human inspection of the real renderer governs charm, coherence, composition, and appeal. Automated evaluators protect mechanical correctness; there is no synthetic beauty score.

## Rendering contract

- Author art on a **400×240 internal Canvas surface**.
- Present at the fixed external/reference **800×480** size using exact **2× integer nearest-neighbor scaling**.
- Keep both internal drawing and final scaling smoothing disabled.
- Snap semantic 800-space presentation coordinates to the 400×240 art grid at the renderer boundary; canonical `TerrariumFrame` coordinates remain hardware-neutral and authoritative.
- Never draw high-resolution 800×480 art and pixelate it afterward.
- Avoid subpixel transforms, antialias-dependent primitives, gradients, blur, bloom, and glossy post-processing.

## Target aesthetic

Finished handcrafted late-16-bit/early-32-bit farming/life-RPG pixel art: warm, cozy, readable, slightly whimsical, and materially grounded. Pixels should be clearly visible and moderately chunky. Silhouettes and clustered shapes matter more than detail count.

The image should read as authored pixel art even when viewed at native 800×480 presentation size—not as smooth vector art with a filter.

## Palette families

Core families:

- **moss green** — rug, foliage, low-saturation natural accents;
- **walnut brown** — furniture, trim, outlines, floor depth;
- **golden amber** — leaves, warm accents, daylight highlights;
- **dusty blue** — blanket, stone, cool environmental accents;
- **cream** — cloth, paper, selective highlights;
- **Moss brown** — warm medium brown body with dark brown shadow/ears and restrained tan highlights.

Use mostly **2–4 stepped shades per material/object**. Neighboring shades should differ enough to form readable clusters. Reserve the lightest values for small deliberate highlights. Reserve the darkest values for selective outlines, contact edges, deep overlaps, and focal facial features.

Avoid neon saturation and large ramps of near-identical shades.

## Pixel-cluster rules

- Build forms from intentional rectangles/stair-steps and connected clusters, not smooth analytic curves.
- Prefer a few coherent clusters over scattered single-pixel noise.
- Texture exists to communicate material: short wood-grain runs, cloth stitches/speckles, leaf clumps, flower pixels, floor scuffs, paper marks, bedding creases.
- Break repetitive tiling with deterministic authored offsets or stable hash-derived variation; never use runtime `Math.random`.
- Keep noisy texture away from Moss's face and interaction contact points.
- One-pixel highlights are accents, not a blanket sparkle layer.

## Perspective and scale

Use a flattened three-quarter/slightly elevated game-world view. Depth comes from vertical ordering, overlap, stepped top/front faces, value separation, and sparse contact shadows—not perspective realism.

Useful art-grid scale conventions at 400×240:

- Moss hero sprite: roughly **40–46 px wide × 30–38 px tall** including ears/tail in active poses;
- movable props: roughly **8–12 px** major dimension;
- furniture edges: typically **2–6 px** thick depending on structural importance;
- contact shadows: usually **1–3 px** tall and narrower than the subject;
- major room zones must remain readable without labels.

The large moss-green rug/open center is a composition anchor and negative-space buffer around Moss.

## Outlines and shading

Use selective dark outlines where they improve silhouette separation or clarify overlapping forms. Do not ring every object uniformly.

Shading is graphical and stepped:

1. dark/contact shade;
2. base color;
3. lighter plane/cluster;
4. optional tiny highlight.

Do not simulate volumetric airbrush lighting. Shadows are sparse, hard-edged, and subordinate to silhouettes.

## Moss sprite language

Moss is a **small expressive brown floppy-eared dog**:

- compact body;
- slightly oversized head;
- floppy asymmetrical ears;
- short planted legs;
- readable tail;
- minimal face with dark eye/nose pixels;
- strong side/three-quarter gameplay silhouette.

The default sprite has **no glasses** and does not depend on accessories for identity.

Prefer side and three-quarter poses. Front-facing presentation should be exceptional and semantically motivated, never the default idle solution.

Required hero-pose vocabulary:

- idle/rest: compact planted stance with restrained breathing/ear/tail change;
- locomotion: left/right mirrored gameplay silhouette with two readable leg keyframes and minimal vertical bob;
- inspect/contact: target-facing head/ear/gaze shift plus a bounded forepaw/lean contact pose;
- pickup: contact first, then transfer into the chest/paw hold;
- carry: rigid object attachment and steadier posture;
- place: stop → lower/contact → release → settle → retract;
- sleep: supported curl into the sleeping nook, partially overlapped by bedding;
- wake: deliberate unfold/stand transition;
- window watch: planted sill-facing observation with quiet posture.

Favor key poses and readable silhouettes over high frame counts.

## Room identity

Preserve the persistent Terrarium room rather than replacing it with a decorative mockup:

- warm wood interior/floor;
- large readable moss-green rug/open center;
- window with curtain framing;
- shelf/bookshelf;
- plants/foliage;
- sleeping bed/nook;
- bowls;
- activity desk/corner;
- all existing persistent interactive objects;
- meaningful foreground shelf/desk/blanket overlaps.

Persistent history remains visible in pixel language: worn routes, object scuffs, sleep compression/creases, window smudges/wet traces, activity papers/marks, and other causal aftermath. These marks must derive from canonical history counters/positions; the renderer may visualize them but not invent history.

## Environmental states

Day, dawn, dusk, and night use finite palette/value shifts rather than smooth high-resolution lighting. Small staged palette steps are preferred to continuous glossy grading.

Rain/mist use sparse integer-grid marks inside the window/environment. Ambient motion stays quiet and must never compete with Moss. No camera shake, random zoom, full-screen particle noise, or bloom.

## Depth and occlusion

Foreground furniture edges and bedding may cover Moss/props when world position implies it. Occlusion should clarify space rather than hide actions. Contact points remain readable.

Depth priority:

1. background wall/window;
2. floor/rug/history marks;
3. world objects;
4. Moss and carried object;
5. foreground shelf/desk/blanket lips;
6. minimal ambient pixel effects where appropriate.

## Motion rules

Canonical behavior, target ownership, and pacing remain outside renderer authority.

- Heartbeat continuation must not restart animation clocks.
- Motion may be deliberately grid-quantized at the 400×240 art boundary, but semantic/presentation interpolation remains deterministic and continuous before quantization.
- Never add random jitter to fake liveliness.
- Anticipation, contact, hold, settle, and recovery should read as distinct key-pose phases.
- Whole-scene motion is prohibited unless explicitly designed later.
- Carried objects remain rigidly attached after transfer.
- Environmental animation is slower/quieter than character acting.

`temporal-render-auditor-r1` still guards its original dangerous defect classes. For integer-grid output, `grid-quantized-temporal-render-auditor-r1` may evaluate endpoint settling from the continuous presentation anchor only when the visible coordinates prove the declared quantization contract. Neither auditor judges artistic quality.

## Acceptance by human visual inspection

A checkpoint should be rejected if the real 800×480 output feels filtered, smooth/vector-like, over-detailed, muddy, neon, glossy, visually noisy, compositionally confused, or if Moss stops being the focal character—even if automated tests pass.

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
