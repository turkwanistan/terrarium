# Terrarium Product Roadmap

Terrarium develops as a normal product. Repository state, live canonical state, evaluation evidence, and direct UAT override this roadmap when they expose a more important concrete weakness.

The post-Iteration-6 roadmap is organized around expanding **causal situation space**, not merely increasing the number of action labels.

## Iteration 7 — Situational Events and Environmental Attention

Make the world initiate meaningful opportunities and interruptions rather than leaving Moss as the sole source of activity.

Target causal structure:

**event → perception → reaction → decision/engagement → aftermath**

Candidate authored events include moving sunlight, a bird outside, rain escalation, thunder, a moth/bug at night, leaf/window contact, first morning light, or an unusually salient sunset.

Requirements:

- events are canonical world state with deterministic occurrence conditions, lifecycle, duration, salience/perceptibility, and spatial context;
- Moss may ignore, briefly orient toward, defer, interrupt for, or actively engage with an event depending on current commitment, opportunity, repetition history, habits/context, and event salience;
- events must not behave like mandatory interrupt handlers that cancel every ongoing activity;
- temporary environmental affordances are allowed when physically meaningful, e.g. a sunlight patch becoming a desirable loaf location and later moving/disappearing;
- the same low-level action may have different meaning because its cause differs: casual window watching, rain watching, bird tracking, thunder investigation, bug following, etc.;
- rendering remains subordinate to authoritative event/world state and preserves the accepted pixel contract;
- deterministic multi-seed evaluation should cover event occurrence, response diversity, ignored/deferred events, interruption bounds, causal follow-through, and repetition control.

Success means the room begins to feel like a place where things happen **to** Moss and his response reveals character through behavior.

## Iteration 8 — Object Identity and Stateful Affordances

Stop treating persistent props as one generic inspect→pickup→carry→place token wearing different art.

Requirements:

- define a small set of object classes/archetypes whose available affordances differ materially;
- object-specific affordance subsets replace a universal interaction graph;
- interactions produce authoritative persistent state transitions that affect later possibilities;
- candidate archetypes include rolling/chaseable objects, cloth/cushion nesting objects, paper/scatter objects, containers/hiding objects, and plant/reactive environmental objects;
- candidate chains include paw→roll→chase→lost/retrieved, tug→drag→rumple→sleep-on, scatter→pile, peer-into→hide/store, or sniff/watch→fallen-leaf reaction;
- habits/history may make particular objects favorites without turning object class into a fixed personality script;
- preserve spatial authority, object identity, replay, migration safety, and renderer authority boundaries;
- evaluate combinatorial affordance breadth, state-transition validity, object-class differentiation, long-run persistence, and absence of generic-object collapse.

Success means object identity materially changes what situations are possible, rather than only changing appearance.

## Iteration 9 — Emergent Situations and Consequence Memory

Once world events and stateful object affordances exist, let their consequences compose across longer horizons.

Requirements:

- Moss can revisit, maintain, exploit, or react to consequences created by prior activity;
- prior arrangements, temporary environmental events, object displacement/state, and learned habits can create later opportunities;
- occasional multi-stage situations may unfold across minutes, hours, or days without hard-coded narrative scripts;
- recognition should come from authoritative world state/history rather than hidden planner memory;
- equivalent present worlds with different causal histories should be able to produce meaningfully different future situations while remaining individually deterministic;
- retain bounded intent/session machinery as long as it can express the needed causal chains cleanly.

Example target shape:

> moth appears → Moss follows it → engages a ball → ball rolls under furniture → moth disappears → much later Moss revisits the area and retrieves or re-engages the displaced ball

Success means richer situations emerge from interacting systems rather than from prewritten quest chains.

## Planning / SBC gate

Do **not** introduce GOAP, a generic planner, Sims-style needs, personality-stat systems, quest logic, or LLM action selection merely because situations become richer.

First push the existing model of **attention + affordances + persistent state + habits + short causal commitments**.

Only propose a more general planning substrate or Self-Building Computer Generation 18 if implementation evidence demonstrates a genuinely reusable limitation that cannot reasonably be expressed or evaluated with Terrarium's existing intent/session model and promoted SBC capabilities. Product complexity by itself is not a substrate deficiency.
