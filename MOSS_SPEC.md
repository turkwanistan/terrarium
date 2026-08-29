# Moss — Godot Presentation Character Lock

This document locks the approved Godot presentation identity for Moss. Repository/runtime authority still governs behavior and state; this file governs how canonical Moss is drawn in the Godot presentation candidate.

## Canonical visual baseline

The approved production baseline is **authored geometry → Godot palette only**.

Every production Moss raster must be generated directly from the accepted geometry in `display/art/moss/*.json`, translating only the authored palette roles through `MOSS_MAP`. Production generation must not add fixed-coordinate facial/chest/fur pixels, must not run pose-safe recoloring, and must not expand, shrink, or otherwise edit the authored silhouette/anatomy.

This deliberately preserves the compact side/three-quarter Moss identity that carried the most charm in the original authored sprites while integrating him into the Godot room palette. Review candidates A/B/C remain historical comparison evidence only and are not production character states.

The later special frontal experiment is explicitly rejected. It made Moss read taller, chest-forward, more humanoid, and anatomically disconnected from the existing walk/inspect vocabulary. It must not be revived as an idle, front pose, or "cute" correction.

## Identity invariants

Moss must remain:

- a small brown-and-cream floppy-eared dog;
- compact rather than tall or long-legged;
- clearly quadrupedal;
- slightly oversized in the head, but not dominated by a giant frontal face;
- short-muzzled while still reading primarily in side/three-quarter gameplay view;
- planted on short paws with a low center of gravity;
- asymmetrical through ears/tail/fur clusters rather than human-like posture;
- visually prominent enough to remain the room's emotional focus;
- readable at the native 400×240 art surface and exact 2× 800×480 presentation.

## Proportion lock

Use the accepted authored Moss frame bounds and anchor vocabulary from `display/art/moss/`. Do not force a human 16×32 convention. In active poses Moss should remain roughly within the established 40–60 px wide / 30–52 px tall source-art envelope depending on tail, ear, and action extension.

The normal read is **horizontal compact body + clearly directed head + short planted legs**. A pose may compress, curl, lean, or extend for an action, but should return to that identity.

## Face and silhouette

- One strong gameplay-facing eye is sufficient in side/three-quarter poses; a second eye must not force a frontal head turn.
- Muzzle remains short and rounded, but projects enough to read as canine.
- Cream blaze/muzzle/chest/paw accents support recognition without turning into a white vertical "shirt" shape.
- Ears remain floppy and asymmetrical, with dark/chromatic depth rather than large symmetrical side panels.
- Tail is a small acting cue, not a constant wag loop.
- Outlines are selective/chromatic; lower/contact edges may be stronger than light-facing edges.

These qualities must come from the accepted authored sprite geometry and palette-role mapping. Do not "improve" them afterward with a generic finishing pass. If richer character art is desired in the future, author it deliberately in the canonical Moss source assets first and review it as an identity change rather than silently painting over generated production rasters.

## Production pose set

The Godot candidate currently derives these presentation frames from accepted authored Moss assets:

- `idle` — stable planted hold; no required breathing loop;
- `walk` — four contact/weight-shift frames; canonical `explore` uses the same locomotion presentation;
- `inspect` — anticipate → contact → hold → recover;
- `nudge` — anticipate → contact → press → hold → recover;
- `rest` — supported quiet pose;
- `loaf` — distinct relaxed supported silhouette;
- `groom` — start → contact → hold → recover;
- `stretch` — ready → extend → hold → recover;
- `sleep` — four settle frames → curled hold;
- `wake` — four authored unfold/stand frames;
- `carry` — canonical carry stages pickup anticipation → contact → lift → hold once, then settles into the stable carry pose;
- `place` — lower → contact → hold/release → recover;
- `look` — bounded orient/react plus ordinary idle/mirroring;
- `window_watch` — ready → planted watch hold.

Pose selection is presentation only. Canonical Terrarium state decides activity, target, position, facing, time, weather, and history.

## Motion law

- Low frame count is preferred to smooth tweened anatomy.
- Contact actions must have readable anticipation/contact/hold/recovery.
- Idle/rest/sleep holds may be completely still.
- Walk may loop; most action sequences should settle into their final pose rather than loop forever.
- Translation may interpolate canonical movement, but body-part deformation must not invent motion.
- No random jitter, constant ear wag, whole-body breathing bob, skeletal smoothing, or camera-relative posing.

## Validated support choreography

Sleep/wake uses authored presentation staging rather than changing canonical movement:

- sleep: open-floor bed gate → climb to mattress → settle behind the front rail → curled supported hold;
- wake: curled hold → rise on mattress → climb out → finish at the same open-floor gate;
- `bed_front_lip.png` is an action-scoped occluder visible only for sleep/wake, so ordinary walking in front of the bed is never incorrectly hidden;
- window-watch keeps its validated bed/window perch staging; ordinary canonical `window` movement remains on the mapped floor-side route.

The staging is visual only. It never changes canonical zone, route, coordinates, activity, or world state.

## Adoption-gate character result

The palette-only promotion is approved. A repository regression test requires every production Moss PNG to equal the corresponding authored JSON geometry translated through `MOSS_MAP` only. With the complete production action vocabulary there are now 50 top-level production Moss PNGs; the production tree is `60ee1774e3d890fadee4783f896e36c117ae0abb3e1334ac4c20c278758a4f86`; production idle remains `b76ab00cfaa8cd22976df443ccef70b1ebe9ee13b22e521dfca52760d7fdc65b`.

Native Godot 4.7.2 palette-only validation first passed spring idle, walk, inspect contact, sleep settle/curled, wake exit, carry, place contact/release, window-watch, rain idle, and warm-night idle. The later action-completeness gate additionally passed nudge press, loaf, groom hold, stretch hold, pickup contact/lift, and settled carry. Across the three idle environmental variants, the palette-only promotion changed 636 rendered pixels per frame and every changed pixel remained inside the expected Moss actor rectangle; the room/background/foreground remained pixel-identical. Evidence: `artifacts/godot-art-gate/moss-palette-only-promotion/native-validation.json` and `artifacts/godot-art-gate/action-completeness/native-validation.json`.

Pickup is presentation choreography, not a new simulation state: canonical `carry` owns object transfer. A separate live motion clock now prevents committed authored action sequences from restarting on every canonical heartbeat while route interpolation remains independently frame-relative.

Do not reintroduce additive generated fur/material richness as a refinement step. Future Moss refinement should happen in the authored source geometry/palette roles and pass the same identity/native gate.

## Regression rejection checklist

Reject a Moss pass if any of these appear:

- tall chest-forward or quasi-bipedal stance;
- frontal face pasted onto a side-view torso;
- legs lengthened to support a front-facing body;
- large symmetrical ears that read like human hair/panels;
- cream chest becoming a vertical humanoid torso stripe;
- idle identity no longer matching walk/inspect/sleep silhouettes;
- Moss shrunk enough that props/room become the emotional focus;
- detail added at the expense of clean canine silhouette;
- generated production pixels that are not directly derived from the authored JSON geometry plus `MOSS_MAP` palette translation.

## Source and generated assets

- canonical authored pose sources: `display/art/moss/*.json`
- Godot production-candidate raster generation: `display/godot_reference_v2/tools/generate_reference_v2.py`
- generated Godot pose rasters: `display/godot_reference_v2/art/moss_*.png`
- presentation selection/integration: `display/godot_reference_v2/scripts/main.gd`
- native validation safety policy: `GODOT_NATIVE_VALIDATION.md`
- palette-only native acceptance evidence: `artifacts/godot-art-gate/moss-palette-only-promotion/native-validation.json`
- action-completeness native acceptance evidence: `artifacts/godot-art-gate/action-completeness/native-validation.json`
