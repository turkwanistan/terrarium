# Visual Style Overhaul Planning Decision — 2026-08-27

## Status

**PLANNING ACCEPTED.** This entry changes the forward product sequence only. It does not replace or mutate the accepted Pixel-Art Overhaul — Iteration 7 runtime checkpoint.

## Trigger

A detailed external visual-art audit was compared against Terrarium's accepted renderer, art direction, room composition, animation conventions, and current source implementation.

The comparison showed that Terrarium has already solved most of the mechanical pixel contract—400×240 source art, exact 2× nearest-neighbor output, deterministic palette states, low-frame acting, spatial authority, persistent history marks, calm event motion—but the finished illustration remains largely procedural JavaScript drawing. That implementation creates a practical ceiling on authored silhouette quality, material richness, organic asymmetry, sprite acting, generalized depth, local lighting, atmospheric motion, seasons, and long-horizon visual transformation.

## Decision

Reprioritize the next Terrarium work so the visual system catches up before deeper simulation expansion:

1. **Iteration 8A — Visual Grammar and Asset Pipeline**
2. **Iteration 8B — Room Recomposition**
3. **Iteration 8C — Moss Sprite Overhaul**
4. **Iteration 8D — Object Identity and Stateful Affordances**
5. **Iteration 8E — Atmospheric World**
6. **Iteration 8F — Seasonal Terrarium**
7. **Iteration 9 — Emergent Situations and Consequence Memory**

The former “Iteration 8 — Object Identity and Stateful Affordances” target is postponed to 8D, not rejected.

## Target visual grammar

The repo now targets a hand-authored late-16-bit life-RPG diorama with:

- 16×16 static-world art/composition grammar;
- continuous canonical movement independent of that grid;
- authored text-addressable pixel assets rather than renderer code as the finished-art source of truth;
- stronger readable silhouettes;
- saturated natural palette behavior rather than uniformly muted cozy color;
- clustered shading and selective chromatic outlines;
- pragmatic overhead/three-quarter perspective;
- declarative depth, foreground occlusion, and Y-ordering;
- low-frame pose-driven Moss animation;
- quiet non-commanding environmental animation;
- cool-night/warm-local-light contrast;
- weather as a whole-scene mood modifier;
- eventual slow canonical seasons;
- persistent visual consequences grounded in actual Moss history.

Terrarium remains a single persistent domestic habitat with one dog. The target is a system-level visual ecology, not copying another game's assets, palette, characters, buildings, UI, map structure, or farming subject matter.

## Source research

The planning input was the external artifact:

`2026-08-27--video-game-art-animation-world-audit.md`

The full audit is **not checked into this repository**. Its implementation-relevant conclusions and caveats are distilled into `VISUAL_STYLE_OVERHAUL.md` and the updated `ART_DIRECTION.md`, so normal development does not depend on a chat attachment. The original audit is only needed when a future session wants its full evidence trail, examples, caveats, or bibliography.

## Authority changes

Updated:

- `terrarium.md` — current product visual intent;
- `ART_DIRECTION.md` — evolved visual law;
- `VISUAL_STYLE_OVERHAUL.md` — detailed migration plan;
- `ROADMAP.md` — new 8A–8F sequence;
- `START_HERE.md` — fresh-session reading order and next work;
- `STATUS.md` — planning status after accepted Iteration 7;
- `plan.md` — immediate implementation target;
- `README.md` — visual-authority discoverability.

## SBC decision

No reusable Self-Building Computer substrate deficiency has been demonstrated. The first implementation should use Terrarium-local asset formats, renderer changes, validation, and visual review tooling. Capability Forge or a new SBC generation is justified only if direct implementation evidence later exposes a genuinely reusable gap that existing promoted capabilities cannot reasonably cover.

**Gen18: NO.**
