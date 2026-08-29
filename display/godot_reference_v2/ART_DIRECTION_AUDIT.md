# Terrarium Godot Reference POC v2 — Art Direction Audit

## Target read

The supplied reference is the visual north star for this POC: a cozy, handcrafted late-16-bit / early-32-bit-inspired life-sim interior with warm timber architecture, saturated accent colors, pragmatic three-quarter furniture, dense but curated props, strong material separation, and a cute expressive dog as the emotional focal point.

The goal is not literal asset copying. The goal is to make Terrarium's room and Moss feel as though they belong in the same visual language.

## Current judgment

The Godot renderer is not the limiting factor. The fixed 400×240 logical surface, integer 2× presentation, nearest-neighbor filtering, layer ordering, weather variants, and character animation path are sufficient for the target look.

The remaining gap is art craft: silhouette design, selective edge weighting, small material clusters, furniture depth, lighting hierarchy, foliage irregularity, and character acting.

After the audit pass, the room is directionally aligned enough that broad composition changes should stop. Future work should be refinement, not redesign.

## Direction now locked

- Warm amber-brown timber with deep chromatic shadow colors, not flat orange wood.
- Beige plaster upper wall + darker wooden lower wall / floor separation.
- Saturated cobalt/royal blue curtains and accessories as the main cool counterpoint.
- Deep green patterned rug as the main floor anchor.
- Warm cream, terracotta/red, blue, and green prop accents.
- Strong dark lower/right/contact edges; weaker or chromatic top/light-facing edges.
- Pragmatic 3/4 asset grammar: shallow visible top planes, frontal readable faces, no isometric convergence.
- Compact contact shadows instead of soft modern blur.
- Pixel clusters and small asymmetries instead of uniform noise or vector-clean geometry.
- Curated lived-in prop groups rather than evenly distributed clutter.
- Moss remains visually prominent and emotionally central.

## What the reference still does better

### 1. Character craft

This is the largest remaining gap.

The reference dog has a short rounded muzzle, oversized expressive head, clearly readable eyes, asymmetric floppy ears, compact torso, stubby planted paws, strong cream facial/chest markings, and a friendly 3/4 presentation. Moss should continue moving toward that level of charm while retaining his brown/cream identity.

Current audit correction: dedicated rounded 3/4 idle, shorter muzzle, both eyes readable, shorter legs, stronger cream blaze/chest/paws, and a compact horizontal torso.

Next character work should favor action-specific authored poses over procedural embellishment.

### 2. Furniture silhouettes

The reference furniture is not built from perfect rectangles. Bedposts, desk edges, bookcase crown/feet, lamp, stool, pots, and shelves use stepped corners, shallow top planes, bevel pixels, and asymmetric wear.

Current audit correction: shallow top planes, selective edge highlights, stronger weighted undersides, rounder bed-post caps, and bookcase feet/crown depth.

Future passes should refine individual asset silhouettes rather than adding more global texture.

### 3. Material rendering

The reference uses clustered highlights/shadows that describe material: wood grain follows planks, cloth folds follow bedding/curtains, foliage highlights follow leaf masses, and ceramic/metal accents use small high-contrast glints.

Current audit correction: wood knots/grain clusters, curtain folds/tiebacks, bed seams/folds, rug fibers/stitches, book labels, plant highlights, and prop glints.

Avoid uniform speckle. Every texture mark should describe form or wear.

### 4. Lighting/value hierarchy

The reference has stronger warm-light-facing edges and darker contact/underside values. Objects feel seated in the room rather than pasted onto it.

Current audit correction: compact furniture contact shadows and selective warm top-edge highlights. Night lighting remains restrained and stepped rather than a large geometric cone.

### 5. Rug/soft-goods detail

The reference rug has a more handcrafted woven edge, pale side tassel/rope clusters, and richer floral stitch motifs.

Current audit correction: chunky pale side tassels and additional stitched motifs. Keep the rug calm enough that Moss remains the focal point.

### 6. Lived-in storytelling

The reference succeeds because prop clusters imply use: bedside plant/books/candle, desk reading tools, bookcase objects, dog toys, bowl, bones, floor books, and plants.

Current audit correction: added bedside plant/books/candle cluster and preserved the desk/bookcase/dog-toy clusters.

Do not increase prop count indiscriminately; improve shape, placement, and material specificity first.

## Do not regress

- Do not return to flat uniform outlines around every asset.
- Do not replace authored pixel clusters with random noise.
- Do not shrink Moss relative to the room.
- Do not reintroduce the long, low, side-profile Godot-specific dog from the first pilot.
- Do not add renderer features or migration plumbing to solve an art-production problem.
- Do not change projection back toward isometric/perspective-diorama rendering.
- Do not make the rug or window overpower Moss.
- Do not use smooth/blurred lighting or scaling that compromises pixel integrity.

## Recommended next visual iteration

One focused character-and-assets pass only:

1. Author a small complete Moss pose set in the new 3/4 character language rather than mixing the new idle with older side-profile action sprites.
2. Refine bed, desk, bookcase, lamp, and major plants as discrete authored sprites/silhouettes.
3. Improve leaf shapes and object-edge asymmetry.
4. Re-evaluate against the supplied reference at actual 800×480 Godot output.

No new functionality is justified until those visual changes stop producing meaningful gains.
