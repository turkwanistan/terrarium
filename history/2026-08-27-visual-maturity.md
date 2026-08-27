# Visual maturity: art direction + motion coherence — 2026-08-27

This is a normal post-Gen17 Terrarium product checkpoint, not Generation 18.

## Goal

Make the 800×480 Terrarium read as one deliberately art-directed storybook diorama and make Moss's movement/actions feel calm, staged, physically grounded, and intentional without moving behavior authority into the renderer.

## Ranked audit findings

Human inspection of the real Canvas and deterministic temporal sequences found six high-impact weaknesses:

1. **Live transition continuity:** a new canonical tick arriving during an in-flight animation could restart from the prior canonical endpoint instead of Moss's currently rendered position, creating a visible teleport.
2. **Generic motion language:** most transitions shared one generic timing/interpolation shape, so actions looked procedural even when trajectories were smooth.
3. **Weak character presentation:** Moss read too much like simple renderer geometry; carry/sleep/contact poses and silhouette were not distinct enough.
4. **Room/material incoherence:** furniture, floor/wall, cloth/paper, shadows, and contact depth did not consistently read as one physical illustration.
5. **Ambient competition:** rain, dust/motes, bobbing, and small procedural effects competed with the primary character action.
6. **Behavioral presentation indecision:** alternating `walk`/`explore` and `carry`/`place` could evade per-action cooldowns and read as ping-pong despite remaining semantically valid.

These are ranked product judgments, not automated aesthetic scores.

## Art direction

`ART_DIRECTION.md` now governs future renderer work. The identity is a **cozy low-resolution storybook diorama** with muted earthy materials, scarce accents, Moss as the clearest focal element, rounded character shape language, quiet structural depth/contact shadows, and a strict motion hierarchy:

1. primary — Moss and directly manipulated objects;
2. secondary — bedding/papers/local contact reactions;
3. ambient — rain/light/a few slow motes.

The motion grammar is the smallest useful subset of **anticipation → movement → contact → settle → recovery**. Objective temporal tools prove correctness; visual inspection still judges warmth, charm, readability, and art-direction coherence.

## Renderer / composition / animation changes

The renderer remains disposable and non-authoritative, but its presentation is substantially more deliberate:

- distance-aware locomotion duration replaces one generic 1.5 s transition;
- locomotion reserves explicit anticipation/travel/settle/recovery windows;
- live canonical updates rebase from Moss's exact currently rendered pixel position;
- inspect faces and leans toward the actual authoritative object;
- pickup visibly transitions object → reach/contact → chest/paw attachment;
- carried objects remain rigidly attached during travel;
- placement stages prepare → lower/contact → settle at the canonical authored slot;
- sleep/wake uses a real curled/compressed silhouette and reversible body deformation instead of an upright sprite plus `z` text;
- walk bob and idle breathing are smaller and calmer;
- Moss gets a stronger tail/body/head silhouette and more consistent contact shadow;
- wood, cloth, paper, foliage, floor/wall, and object shadows now share a governed material/value language;
- baseboard, floor seams, window light, furniture thickness, and contact shadows improve depth without adding renderer-owned state;
- rain and motes are reduced in count/speed/contrast so ambient motion stays subordinate.

## Bounded canonical behavior change

The simulation remains probabilistic and deterministic. No renderer-side behavior engine or canned routine was added.

Recent-action suppression now also recognizes semantic families:

- movement family: `walk`, `explore`;
- manipulation family: `carry`, `place`.

This prevents alternating members of a family from bypassing cooldowns. Normal launchers also use the server's 3-second world cadence instead of overriding it to 1 second.

Seed 1701 / 500 before → after:

- action classes: `10 → 10`;
- entropy: `3.151553 → 3.103385` bits;
- consecutive movement pairs: `50 → 19`;
- immediate zone reversals: `9 → 5`;
- maximum consecutive movement actions: `4 → 2`;
- adjacent manipulation pairs: `10 → 7`;
- maximum manipulation burst: `4 → 3`;
- moved objects after 500: `6 → 6`.

Diversity remains healthy; the change reduces visual indecision rather than scripting a routine.

## Objective temporal evidence

A new deterministic consecutive-update continuity probe demonstrates the largest defect directly in the actual Canvas renderer:

- legacy rebasing instantaneous jump: **352.907594 px**;
- accepted rendered-position continuity jump: **0 px**.

Repeated raw deterministic `left_walk` capture remained byte-identical at SHA256 `8853ad450bb5cac36ea5273b24de069b8ec9656ede77d7787574d1b7063992d5`.

The already-promoted `temporal-render-auditor-r1` was resolved at content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1` and executed independently in the isolated Lab against **15 real deterministic Canvas sequences plus real RAF pacing: 16/16 PASS**.

Representative metrics:

- left traversal: final progress 1.0, reversals 0, facing mismatches 0, endpoint-speed ratio `0.016818`;
- right/arrive traversal: final progress 1.0, reversals 0, facing mismatches 0, endpoint-speed ratio `0.037951`;
- carried traversal: attachment span `0`, endpoint-speed ratio `0.033269`;
- RAF: 156 intervals, median `16.7 ms`, max `16.8 ms`, zero >50 ms stalls.

The retained hero reel covers left/right traversal, arrive+settle, quiet idle, window watching, rain at window, object inspection, pickup, carried movement, placement, sleeping, waking, activity-corner use, populated/lived-in room, rain control, deterministic repeat equality, and real RAF pacing. Compact evidence lives under `artifacts/visual-maturity-compact/`; raw browser transports were discarded after compaction.

## Behavior / technical regression

- pytest: **18/18 PASS**;
- JavaScript syntax: **PASS**;
- Python 3.10 syntax compatibility: **PASS** across 22 project/test Python files;
- technical evaluator: **PASS**;
- exact snapshot + subsequent-event replay: **PASS**; canonical/replayed hash `5d3503fac94f66642ed338045a9f9ee15db83fbae47fcee29c94995067691fd0`;
- behavior evaluator seed 1701 / 500: **PASS**;
- promoted `simulation-behavior-auditor-r1` independently reused in isolated Lab: sequence integrity PASS, 10 action classes, entropy `3.103385`, 97 configured object interactions.

Primary compact evaluation: `artifacts/visual-maturity.json`.

## Snapshot

Exactly one meaningful deterministic development snapshot was created:

- snapshot: `20260827T165449319827Z-visual-maturity`;
- seed **1701**, tick **180**;
- frame SHA256 `9a422b0de25ffa7311a1b86e315379189ae485485edc79bc02e948d0959a1487`;
- renderer SHA256 `a523186cab91e614034eb6593e3ea3db4b558ac448ca5d1c640cd43fb7362807`.

Tick 180 intentionally captures a dawn activity-corner pickup after meaningful accumulated bedding/work/window history. It shows the stronger Moss silhouette, carried-object posture, governed materials, grounding, and lived-in composition instead of using the old neutral/default tick. The stored frame was opened and visually inspected through the real Canvas at an exact 800×480 viewport.

## SBC conclusion

The accepted SBC substrate was sufficient: project preflight/context, existing promoted behavior/temporal auditors, isolated Lab execution, deterministic browser evidence, snapshots, replay, and mediated project Git were enough. No new capability was forged and no permanent MCP surface was added.

**No Gen18 warranted.**

## Runtime boundary

Canonical living Moss state remains outside Git under the user-owned runtime directory. Development verification used an isolated temporary data directory and did not touch that database. A mediated development service is not a substitute for canonical LAN deployment; only an actually verified host-owned runtime may be reported as deployed.
