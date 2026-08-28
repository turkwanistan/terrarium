# Terrarium — Persistent Creature Display Plan

**Initial target:** 800×480 desktop terrarium  
**Initial renderer:** PC browser/window  
**Persistent host:** always-on home server / OptiPlex-class machine  
**Eventual hardware:** inexpensive dedicated 800×480 touch display, preferably ESP32-S3-class  
**Core principle:** the creature's identity and life persist independently of any display

---

# 1. Concept

Terrarium is a **low-maintenance persistent artificial creature living in a small visible world**.

It is not a Tamagotchi. There are no mandatory feeding schedules, punishment for being away, or constant chores.

The creature continues to live whether anyone is watching it.

Over time it can:

- sleep;
- wander;
- inspect things;
- collect objects;
- move possessions around;
- form routines;
- prefer some objects, places, times, or environmental conditions;
- avoid things associated with unpleasant experiences;
- develop habits;
- accumulate visible changes in its habitat;
- remember meaningful events;
- occasionally behave in ways that feel specific to its own history.

The goal is not to simulate a full life.

The goal is to create enough **continuity, visible history, and accumulated preference** that the creature feels like the same little entity every time you look at it.

---

# 2. Product thesis

The most important feeling Terrarium should create is:

> "Something has been happening here while I was gone."

Examples:

- the creature moved a blue object beside its bed;
- it has started spending evenings near the window;
- it keeps returning to one corner;
- a shelf is slowly filling with things it found;
- it avoids a place associated with repeated unpleasant events;
- rain has gradually become one of its favorite conditions;
- some odd repeated pattern becomes a recognizable habit.

Those behaviors should be grounded in actual stored history rather than invented when someone asks about them.

---

# 3. Core architectural rule

**The display is not the creature.**

The creature's canonical state lives on the persistent host.

The display only renders the world and sends interaction events.

```text
┌───────────────────────────────────────────────────┐
│ Persistent Terrarium host                        │
│                                                   │
│ clock                                             │
│ simulation                                        │
│ creature state                                    │
│ objects                                           │
│ learned associations                              │
│ routines                                          │
│ event history                                     │
│ snapshots                                         │
│ reasoning / reflection hooks                      │
└────────────────────────┬──────────────────────────┘
                         │
                  TerrariumFrame
                         │
          ┌──────────────┴──────────────┐
          │                             │
  PC renderer, v0              dedicated display later
  browser 800×480              ESP32-S3 / similar
```

If the display dies, the creature does not.

If the display is replaced, the same creature wakes up on the new hardware with the same:

- history;
- possessions;
- preferences;
- routines;
- relationships;
- world state.

---

# 4. v0 strategy

Start for **$0 on the PC**.

Build the complete product around a fixed **800×480 logical viewport**.

The PC version is not a disposable prototype. It is the **reference renderer** for the later physical display.

The logical display resolution should never change.

The desktop window can scale the 800×480 image to 1.5× or 2× for convenience, but all layout and animation remain authored for the eventual physical screen.

---

# 5. v0 world

Use one small persistent habitat.

Suggested zones:

```text
┌──────────────────────── 800 px ─────────────────────────┐
│                                                        │
│ WINDOW / WEATHER                    COLLECTION SHELF    │
│                                                        │
│                                                        │
│                 OPEN LIVING SPACE                      │
│                                                        │
│                                                        │
│ SLEEPING NOOK                         ACTIVITY CORNER   │
│                                                        │
└──────────────────────── 480 px ─────────────────────────┘
```

The habitat should feel like a **digital diorama**, not an application UI.

Avoid permanent:

- status bars;
- meters;
- menus;
- stat panels;
- health bars;
- giant dialogue boxes.

A hidden debug overlay is fine.

---

# 6. Visual direction

Recommended starting style:

## Cozy pixel / low-resolution illustrated diorama

Reasons:

- readable on a small screen;
- expressive without requiring complex art;
- cheap to animate;
- easy to port to embedded hardware;
- visible changes are easy to notice;
- imperfections can feel intentional;
- sprite memory requirements remain manageable.

A useful art strategy is to author at a lower internal resolution and upscale cleanly.

For example:

```text
source scene: 400×240
display:      800×480
scale:        2×
```

The final output remains exactly 800×480.

---

# 7. Creature behavior

v0 only needs a small expressive vocabulary.

Actions:

- idle;
- walk;
- sit;
- sleep;
- wake;
- inspect;
- carry;
- place object;
- look outside;
- explore;
- rest;
- react to something unusual.

Expressions:

- neutral;
- curious;
- content;
- sleepy;
- startled;
- uncertain;
- excited;
- annoyed.

The creature should not constantly perform.

Long periods of ordinary behavior make unusual moments more meaningful.

---

# 8. Persistent visible history

The habitat itself should become a record of the creature's life.

Examples:

- objects remain where they were placed;
- collected items fill a shelf;
- a preferred sleeping object stays near the bed;
- favorite places become visually lived-in;
- the creature repeatedly rearranges certain things;
- a journal or wall accumulates marks;
- a little map gradually fills;
- decorations appear because of repeated interests;
- habitual movement routes may become subtly worn;
- recurring events can create small environmental artifacts.

The normal screen should not explain all of this.

The user should first **notice** something, then optionally inspect why it happened.

---

# 9. Persistent world engine

Recommended first implementation:

- Python;
- SQLite;
- append-only JSONL event log;
- deterministic seeded PRNG;
- small HTTP API;
- WebSocket or Server-Sent Events for display updates;
- strongly typed state/event contracts;
- pytest.

The host continuously runs:

- world clock;
- simulation ticks;
- autonomous action selection;
- state transitions;
- learning;
- routine detection;
- event logging;
- snapshots.

The renderer may be completely closed without stopping life.

---

# 10. World state

Canonical state should include:

## Creature

- unique ID;
- birth timestamp;
- age;
- location;
- current activity;
- energy;
- comfort;
- curiosity;
- social interest;
- novelty preference;
- familiarity preference;
- possession references;
- learned associations;
- current routine influences.

## Habitat

- world time;
- zones;
- object positions;
- object states;
- light/time-of-day;
- weather-like simulated conditions;
- environmental state;
- persistent visual changes.

## History

- append-only events;
- periodic snapshots;
- learned associations;
- routines;
- reflections;
- versioned simulation rules.

---

# 11. Drives

Do not define personality primarily with prose.

Use a small number of numeric drives.

For example:

```text
energy
comfort
curiosity
social_interest
novelty_seeking
familiarity_seeking
mastery
```

These influence action selection.

They should not be visible as Tamagotchi meters.

They exist to make behavior coherent.

---

# 12. Learned associations

The creature should learn associations between contexts and outcomes.

Examples:

```text
rain               +0.32
window             +0.41
blue_stone         +0.57
east_corner        -0.26
evening            +0.18
Tuesday            +0.09
loud_noise         -0.44
```

Do not directly set:

```text
likes_rain = true
```

Instead, actual experiences gradually change the underlying association.

A higher-level explanation may eventually infer:

> "I think I like rain."

That statement is meaningful only because the underlying history exists.

---

# 13. Memory model

Keep memory types explicit.

## Event memory

What actually happened.

Examples:

- object found;
- creature startled;
- rain started;
- creature slept somewhere;
- object moved;
- interaction occurred.

## Association memory

Learned relationships between:

- objects;
- places;
- times;
- environmental conditions;
- people;
- outcomes.

## Routine memory

Repeated patterns such as:

- sleeps near the window after dusk;
- inspects the shelf in the morning;
- carries objects toward one corner.

## Reflection memory

Occasional higher-level interpretation derived from many events.

Example:

> "The window feels safer at night."

Reflections remain linked to their source evidence.

---

# 14. Event ledger

Every meaningful event should be recorded.

Example:

```json
{
  "event_id": "evt_0184921",
  "tick": 184921,
  "timestamp": "2026-09-04T19:12:23-04:00",
  "type": "object_inspected",
  "actor": "creature",
  "object": "blue_stone",
  "context": [
    "evening",
    "rain"
  ],
  "effects": {
    "curiosity": -0.08,
    "blue_stone_valence": 0.03
  }
}
```

Requirements:

- append-only;
- ordered;
- schema-versioned;
- inspectable;
- content-hashable if useful;
- replayable;
- derived memories retain source event references.

---

# 15. Snapshots and replay

The system should periodically write compact world snapshots.

To reconstruct history:

```text
snapshot
+
subsequent events
=
exact later state
```

A deterministic test world should support:

```text
seed + initial state + event/rule version
→ same resulting world
```

This enables:

- debugging;
- historical inspection;
- behavior comparison;
- safe simulation experiments;
- investigating why a preference developed.

---

# 16. Explainability

A developer/debug command should be able to answer questions such as:

```text
Why does the creature prefer the window?
```

Example output:

```text
window association: +0.41

27 contributing events

largest positive contributors:
  8 rain-observation events
  6 successful curiosity events
  9 calm/rest events

negative contributors:
  4 startle events
```

Likewise:

```text
Why does it sleep beside the blue stone?
```

The answer should come from actual behavior history.

---

# 17. Action selection

Keep v0 understandable.

A simple system is preferable to an opaque agent.

Each possible action gets a utility score based on:

- drives;
- learned preferences;
- routines;
- current environment;
- recent repetition;
- novelty;
- bounded randomness.

Example:

```text
inspect_blue_stone       0.61
sleep                    0.42
look_through_window      0.68
wander                   0.34
move_leaf                0.27
```

Select probabilistically among the stronger candidates rather than always taking the absolute maximum.

This preserves both coherence and variation.

---

# 18. Avoid repetitive behavior

A major failure mode will be obvious loops.

Use:

- repetition penalties;
- action cooldowns;
- recent-history suppression;
- satiation;
- novelty bonuses;
- bounded random variation;
- changing environmental opportunities.

The creature should be capable of forming routines without becoming mechanically repetitive.

---

# 19. Time

Real time passes continuously.

Useful time scales:

- real clock;
- day/night;
- weekday;
- seasons later;
- time since last interaction;
- time since last event;
- duration of routines.

The simulation should not need to execute every second while idle.

It can schedule or batch low-interest periods efficiently.

When the process restarts after downtime:

```text
last saved timestamp
→ current timestamp
→ bounded catch-up simulation
```

Do not generate millions of fake minute-by-minute events just because the machine was off.

---

# 20. Renderer contract

The server exposes a hardware-neutral semantic frame.

Example:

```json
{
  "frame_version": 1,
  "tick": 184921,
  "world_time": "2026-09-04T19:12:23-04:00",
  "lighting": "dusk",
  "weather": "rain",
  "creature": {
    "x": 317,
    "y": 348,
    "facing": "right",
    "pose": "sitting",
    "activity": "watching_window",
    "expression": "content"
  },
  "objects": [
    {
      "id": "blue_stone",
      "x": 401,
      "y": 362,
      "state": "placed"
    }
  ]
}
```

The renderer handles:

- sprite animation;
- interpolation;
- particles;
- ambient effects;
- transitions.

The world server decides what is actually happening.

---

# 21. PC renderer

Recommended v0:

- HTML5 Canvas;
- TypeScript or lightweight JavaScript;
- PixiJS if useful;
- fixed logical 800×480 viewport;
- optional integer scaling;
- no responsive mobile-first design.

The browser should be able to:

- disconnect;
- reconnect;
- request current authoritative frame;
- continue rendering without mutating canonical world state.

---

# 22. Renderer independence

The same semantic world frame should eventually support:

```text
TerrariumFrame
     │
     ├── WebCanvasRenderer
     │
     └── LVGLRenderer
```

This is the core migration strategy.

Do not stream desktop screenshots to the future hardware.

Do not make the hardware run the whole simulation.

---

# 23. Interaction

v0 interactions should be sparse.

Possible PC interactions:

- click creature;
- click object;
- click window;
- offer one object;
- inspect journal/history through a separate UI;
- ask a question through a separate chat/interface.

Avoid turning the terrarium screen into a control panel.

Later, physical touchscreen events map to the same world events.

---

# 24. Optional conversational layer

Conversation is useful, but it is not the creature's life engine.

Questions might include:

> What did you do while I was gone?

> Why are you always near the window?

> What's your favorite thing in here?

> Did anything interesting happen today?

Answers should be grounded in:

- event history;
- current state;
- learned associations;
- routines;
- reflections.

The system should never invent an event and then save that invented event as history.

---

# 25. Absence recap

A useful feature is a compact summary generated from events since the last interaction.

Input:

- last interaction timestamp;
- meaningful new events;
- changed preferences;
- changed routines;
- newly acquired/moved objects;
- unusual events;
- current activity.

Example:

> "I slept by the window again, moved the blue stone beside my bed, and spent a while watching the rain. I think I'm starting to like it there."

Every statement should map back to actual stored state/events.

---

# 26. Project structure

Suggested repository:

```text
terrarium/
│
├── README.md
├── START_HERE.md
├── STATUS.md
├── plan.md
├── pyproject.toml
│
├── terrarium/
│   ├── world/
│   │   ├── engine.py
│   │   ├── clock.py
│   │   ├── actions.py
│   │   ├── drives.py
│   │   ├── associations.py
│   │   └── routines.py
│   │
│   ├── state/
│   │   ├── models.py
│   │   ├── events.py
│   │   ├── store.py
│   │   └── replay.py
│   │
│   ├── api/
│   │   ├── server.py
│   │   └── frame_contract.py
│   │
│   └── cognition/
│       ├── context.py
│       ├── reflection.py
│       └── explanations.py
│
├── display/
│   ├── web/
│   └── assets/
│
├── hardware/
│   ├── README.md
│   ├── frame_contract.md
│   └── esp32-s3/
│
├── tests/
├── evaluations/
└── artifacts/
```

---

# 27. Development phases

## Phase 0 — Contracts and skeleton

Build:

- repository;
- state schema;
- event schema;
- fixed 800×480 render contract;
- deterministic seed support;
- minimal world process;
- minimal browser renderer.

Acceptance:

- renderer opens at exactly 800×480 logical pixels;
- renderer reconnects safely;
- restart preserves a trivial state.

---

## Phase 1 — Something visibly alive

Build:

- one creature;
- basic sprite animation;
- four habitat zones;
- walk;
- idle;
- sleep;
- day/night;
- autonomous action selection.

Acceptance:

- leave it running for one hour;
- behavior changes without input;
- closing the browser does not pause life;
- reopening shows the advanced world state.

---

## Phase 2 — Persistent objects

Build:

- 5–10 objects;
- inspect;
- carry;
- place;
- persistent coordinates;
- collection shelf;
- simple environmental changes.

Acceptance:

- the habitat is visibly different after extended runtime;
- restart preserves object placement;
- replay recreates the same arrangement.

---

## Phase 3 — Learned preferences

Build:

- association learner;
- reinforcement from events;
- preferences for objects/places/context;
- provenance report.

Acceptance:

- repeated experience produces measurable preference change;
- preference can be traced to source events;
- behavior changes accordingly.

---

## Phase 4 — Routines

Build:

- repeated pattern detector;
- time/place/action routines;
- routine confidence;
- gradual reinforcement and decay.

Acceptance:

- repeated experience can create a routine;
- disrupted experience can weaken it;
- routine influences behavior without hard-coded scripts.

---

## Phase 5 — Grounded conversation

Build:

- check-in;
- absence recap;
- explanation of preference;
- explanation of routine;
- optional reflections.

Acceptance:

- all factual claims can be traced to state/events;
- no fabricated history is persisted.

---

## Phase 6 — Long-running experiment

Let the creature live.

Run:

- one real-time instance;
- one accelerated deterministic test instance.

Observe for several days.

Track:

- event volume;
- action diversity;
- preference growth;
- routine formation;
- repetitive loops;
- state growth;
- recovery behavior;
- performance.

Avoid constantly rewriting behavior rules.

Gather evidence first.

---

# 28. Hardware fork gate

Do not buy hardware simply because the software works.

Buy hardware when this becomes true:

> **You voluntarily leave the terrarium open and occasionally check what the creature is doing.**

If the PC version does not create that feeling, a physical screen will not fix it.

---

# 29. Preferred hardware architecture

The dedicated device should contain:

- display;
- microcontroller;
- Wi-Fi;
- touch;
- local sprite/assets;
- transient animation state.

The persistent host should continue to contain:

- identity;
- event history;
- world state;
- learned preferences;
- routines;
- possessions;
- reflections;
- relationships.

---

# 30. Preferred hardware option — 4.3" ESP32-S3 touch display

A small **4.3" 800×480 ESP32-S3 capacitive-touch display** is the preferred final form factor.

Why:

- exact 800×480 target;
- physically small enough to feel like a little contained world;
- inexpensive;
- Wi-Fi;
- touch;
- PSRAM;
- microSD on many variants;
- LVGL support;
- low power;
- no Linux desktop;
- easy future sensor expansion.

A Waveshare ESP32-S3 4.3" touch board is a strong example.

Typical relevant specifications:

- ESP32-S3;
- dual-core up to 240 MHz;
- 800×480 IPS LCD;
- capacitive touch;
- 8 MB-class PSRAM depending on model;
- 16 MB-class flash depending on model;
- Wi-Fi/BLE;
- microSD/TF;
- GPIO/I2C and other expansion interfaces.

Reference:

https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3

---

# 31. Convenient local hardware option — 7" ESP32-S3

A 7" 800×480 ESP32-S3 touch board is useful if locally available.

Pros:

- same logical resolution;
- easier development;
- larger screen;
- inexpensive integrated hardware;
- touch;
- easy desk prototype.

Cons:

- less "tiny terrarium";
- more like a dashboard or digital photo frame.

A 7" board can still be excellent for development even if the eventual final body is 4.3".

---

# 32. Raspberry Pi fallback

Use a Raspberry Pi only if the embedded renderer becomes an unnecessary distraction.

Advantages:

- reuse browser renderer almost unchanged;
- easier debugging;
- Linux ecosystem.

Disadvantages:

- more expensive complete system;
- longer boot;
- SD-card/filesystem concerns;
- more power;
- significantly more computer than the endpoint needs.

The Pi is an escape hatch, not the preferred final architecture.

---

# 33. ESP32 migration

Do not port the world engine.

Only implement a new renderer.

```text
Terrarium host
     │
     │ semantic frames/events
     ▼
ESP32-S3
     │
     ├── asset cache
     ├── local sprite animation
     ├── interpolation
     ├── touch handling
     └── LVGL display
```

The ESP32 may render at 30–60 FPS.

The host only needs to send meaningful updates at roughly 1–5 Hz or on state transitions.

Example:

```text
host:
walk from sleeping_nook to window over 2.8 seconds

display:
animate locally for 2.8 seconds
```

Do not stream 800×480 bitmaps over Wi-Fi.

---

# 34. Offline behavior

If the display loses Wi-Fi:

1. finish the current visual animation;
2. stop making world-authoritative decisions;
3. retain the last rendered scene;
4. optionally show a subtle offline indicator after a delay;
5. reconnect;
6. request authoritative current state;
7. resynchronize.

The device should never invent canonical history while disconnected.

---

# 35. Touch on hardware

Touch actions become events sent to the host.

Examples:

```text
tap creature
→ attention event

hold creature
→ affectionate interaction

tap object
→ inspection/interaction event
```

Flow:

```text
touch
→ device event
→ host validates
→ world changes
→ new TerrariumFrame
→ renderer updates
```

The touchscreen does not directly mutate durable world state.

---

# 36. Future physical sensors

Only after the dedicated display works well.

Potential additions:

- ambient light;
- room temperature;
- humidity;
- motion/presence;
- microphone with local event detection;
- simple speaker;
- NFC-tagged physical objects;
- nearby BLE beacons.

External observations should become ordinary world events.

Example:

```text
real_room_darkened
dog_bark_detected
user_entered_room
rain_sensor_triggered
physical_object_presented
```

The same event/memory system can learn associations from them.

---

# 37. Debug tools

The normal display should remain uncluttered.

A hidden developer overlay can show:

- tick;
- current action;
- current drives;
- strongest associations;
- action candidates;
- current routine;
- simulation seed;
- event IDs;
- network latency;
- renderer FPS.

A separate desktop inspector can provide:

- event timeline;
- object history;
- association graph;
- routine history;
- snapshot browser;
- replay;
- behavior comparisons.

---

# 38. Evaluation

## Technical metrics

Track:

- deterministic replay success;
- persistence/restart success;
- event/state consistency;
- renderer synchronization;
- API/frame payload size;
- host CPU/RAM;
- database growth;
- event-log growth;
- hardware memory usage later;
- hardware FPS later.

## Behavioral metrics

Track:

- action diversity;
- action repetition;
- number of meaningful learned associations;
- preference stability;
- preference decay;
- routine formation;
- routine persistence;
- environmental sensitivity;
- behavior changes tied to actual experience.

## Product metrics

The most useful questions:

- Did you voluntarily check on it?
- Did you notice that the room had changed?
- Did you notice a habit before reading debug data?
- Did the evidence explain the habit?
- Did anything feel unexpectedly specific to this creature?
- Did it feel alive without demanding attention?

---

# 39. Anti-goals

Terrarium should not become:

- a needy virtual pet;
- a survival game;
- a pet-care simulator;
- a chatbot with a sprite;
- a procedurally generated RPG;
- a robotics project;
- a home automation dashboard;
- a stats-monitoring screen;
- a constant stream of LLM-generated narration.

The creature should communicate through **behavior first**.

Language is secondary.

---

# 40. v0 completion checklist

Terrarium v0 is complete when:

- [ ] One 800×480 habitat is pleasant enough to leave open.
- [ ] The creature continues living when the renderer is closed.
- [ ] Process restart preserves canonical state.
- [ ] Event history is append-only and inspectable.
- [ ] Deterministic test seeds replay consistently.
- [ ] Creature can autonomously walk, rest, inspect, carry, and place objects.
- [ ] The habitat visibly accumulates changes.
- [ ] At least one preference emerges from repeated experience.
- [ ] The preference can be explained using source events.
- [ ] At least one routine emerges from repeated experience.
- [ ] The routine can weaken when experience changes.
- [ ] The creature avoids obvious repetitive loops.
- [ ] "What happened while I was gone?" is grounded in real events.
- [ ] The renderer consumes a hardware-neutral `TerrariumFrame`.
- [ ] No canonical creature state is stored exclusively in the renderer.
- [ ] The same creature can later move to another display without losing history.

---

# 41. Recommended execution order

```text
1. Create Terrarium repository
       ↓
2. Define state/event/frame contracts
       ↓
3. Build fixed 800×480 empty habitat
       ↓
4. Add creature + continuous world clock
       ↓
5. Add autonomous movement/rest
       ↓
6. Add persistence + event ledger
       ↓
7. Add replay
       ↓
8. Add persistent movable objects
       ↓
9. Add learned associations
       ↓
10. Add routines
       ↓
11. Add explainability
       ↓
12. Add grounded check-in / absence recap
       ↓
13. Let it run for several days
       ↓
14. Decide whether it is genuinely compelling
       ↓
15. Buy small dedicated display
       ↓
16. Implement second 800×480 renderer
       ↓
17. Same creature wakes up on hardware
```

---

# 42. Recommendation

Spend **$0 first**.

Build Terrarium at exactly **800×480** on the PC while keeping the creature's actual life on the persistent host.

Do not buy a display until the software creature itself becomes something you enjoy checking.

If it works, move the **same creature** to a small ESP32-S3 touchscreen.

The most important milestone is not:

> "We got a sprite running on an ESP32."

It is:

> **"This creature lived on my PC for weeks, and when I moved it into a small physical display it woke up with the same room, possessions, habits, memories, preferences, and history."**

That is the Terrarium.


---

# 43. Current world law — situations and selective attention

Post-v0 Terrarium now treats environmental situations as canonical world state. The room may create bounded opportunities independently of Moss: moving sunlight, outside visitors, weather escalation, brief sounds/contact, and small night activity. These events have deterministic occurrence/lifecycle and spatial context.

They are **opportunities, not commands**. Moss may ignore, orient, defer, rarely interrupt a low-commitment activity, approach, engage, or recover based on current commitment, salience, recent repetition, habits/context, and deterministic attention choice. High-commitment object sessions, possession continuity, supported sleep, and spatial authority remain protected.

The governing causal pattern is:

```text
event → perception / attention → reaction or defer → engagement / decision → aftermath
```

Temporary event-created affordances must be authoritative. A moving sunlight patch, for example, exists at a real canonical walkable coordinate while active and ceases to be usable when it moves or expires. The renderer may visualize an event but may never invent its occurrence, target, preference impact, or causal history.

This law intentionally reuses the existing bounded action vocabulary when possible. A window-watch or loaf can mean something different because its **cause** is different; Terrarium should increase causal situation space before multiplying verbs or adding a generic planner.
