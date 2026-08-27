# Terrarium art direction

This document governs the reference 800×480 renderer. Objective temporal evaluators prove correctness; visual judgment still decides whether the scene is charming, readable, and coherent.

## Visual identity

Terrarium is a **cozy low-resolution storybook diorama**: one small room, hand-placed and softly worn, with Moss as the clear focal character. Shapes are chunky enough to read at 800×480, details are sparse, and history appears as physical traces rather than UI.

- **Cozy** = warm neutrals, low glare, soft contact shadows, breathing room, calm motion.
- **Lived-in** = a few persistent scuffs, creases, moved objects, and work traces with visible causes.
- **Natural** = moss/wood/cloth/stone families share muted earthy values; nothing is neon or plasticky.
- **Magical** = restrained warm light, glass glints, weather, and rare tiny motes—not particle spectacle.
- **Not** a dashboard, vector icon set, noisy procedural demo, flat clip-art room, or constantly animated game scene.

## Palette

Core habitat families:
- wall / plaster: warm desaturated taupe;
- floor / trim / furniture: deep walnut and umber;
- cloth / paper: oat, flax, faded gold;
- foliage / rug: muted sage and lichen;
- stone / glass: cool slate and dusty blue-green.

Moss:
- body: lichen green;
- head/high plane: lighter sage;
- underside/muzzle: warm flax;
- deepest features/outline accents: charcoal olive.

Accents are scarce: amber leaf, red thread, blue stone, glass star. An accent should occupy much less area than Moss.

Value hierarchy: Moss and the active contact area are clearest; furniture is one step quieter; accumulated aftermath is quieter again. Dawn/day are softly warm, dusk shifts mauve/amber, night shifts blue-charcoal with localized warm glow, and rain cools the window rather than the whole room.

## Shape language

Moss uses rounded, bottom-heavy forms: large tail, compact body, slightly oversized head, short planted legs, pointed ears softened by rounded joins. The silhouette must remain recognizable without facial features.

Furniture uses broad rectangles with softened corners and visible thickness. Organic items use asymmetry and curves. Avoid arbitrary tiny geometry, razor-thin lines, and mixed illustration vocabularies.

Edges are mostly fill-defined. Use 1–3 px dark accents only for material seams, object definition, or important facial features; do not outline everything.

## Depth and composition

The frame is an illustration with three layers:
1. **background** — wall, window view, shelf back, light;
2. **midground** — floor, bed, rug, desk, objects, Moss;
3. **foreground** — blanket lip / occasional near-edge framing and contact overlap.

Objects touching a surface receive a small contact shadow. Furniture has a quiet cast/contact shadow. Overlap should explain depth; avoid tangencies where Moss or objects merely kiss an edge. The open center remains negative space for readable traversal.

## Materials

- **wood**: dark walnut base, one warmer top plane, small shadow underneath; no random grain noise;
- **cloth/bedding**: broad matte shapes, folds only where history/contact justifies them;
- **glass**: cool transparent value shifts and sparse glints, never bright white outlines;
- **stone/shell/seed**: one base fill plus one small plane/highlight;
- **paper**: warm flax, thin umber edge, low-contrast marks;
- **foliage**: muted sage clusters with large leaf shapes;
- **floor/wall**: large quiet value fields; texture is structural, not speckled noise.

## Motion hierarchy

1. **Primary** — Moss and an object Moss is actively manipulating.
2. **Secondary** — bedding compression, paper response, object settle, local contact shadow changes.
3. **Ambient** — rain, window light, a few slow motes.

Primary motion gets the largest displacement and clearest timing. Secondary motion stays local. Ambient motion must never make the eye leave Moss.

## Motion grammar

Actions use the smallest useful subset of **anticipation → movement → contact → settle → recovery**.

- **walk**: orient/plant → ease into locomotion → stable travel → decelerate → plant/settle;
- **inspect**: face target → small lean → hold/contact → recover;
- **carry**: orient/reach → object contact → bind object to a clear chest/paw hold → recover into locomotion;
- **place**: stop/prepare → lower → surface contact → release → object settle → retract;
- **window**: arrive → settle at sill → quiet forward gaze → calm departure;
- **sleep**: arrive → compress into nook → curl/settle → slow breathing; wake reverses deliberately rather than popping upright.

Do not use motion merely because time is passing. Idle gestures are slow and sparse. No whole-scene camera movement, random jitter, procedural zoom, or uncontrolled randomness.
