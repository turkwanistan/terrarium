# Pixel-Art Overhaul — Iteration 8D: Object Identity and Stateful Affordances

**Date:** 2026-08-28  
**Status:** ACCEPTED product checkpoint  
**Snapshot:** `20260828T112207258140Z-pixel-art-overhaul-iteration8d`  
**Seed/tick:** `1701 / 10080`  
**Semantic frame SHA256:** `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`  
**Renderer JS SHA256:** `f8e12181a18c2616fdeb8dae1ee5a0453fab6ba3a5ab88912782e497e35cb701`  
**Authored-art tree SHA256:** `ed1fee4cd060519267d131837ab45772754108c1c2eaa4c9a9c65322bce08d9a`

## Product weakness addressed

After the accepted 8B room and 8C Moss sprite overhaul, the six persistent movable objects were the clearest remaining generic system. They had different names and colors, but most of them still passed through effectively the same inspect/nudge/carry/place graph. Object history therefore changed coordinates more reliably than it changed possibility.

Iteration 8D makes **object identity authoritative**. The same Moss action vocabulary now means different things depending on the object, object state persists across later decisions/restart/replay, and authored state variants make that history visible.

## Canonical object identity

The additive schema is `terrarium.object-affordances.v1`; behavior rules advance to `terrarium-rules-v7-object-identity` while the accepted deterministic RNG stream, `terrarium.habits.v1`, `terrarium.situational-events.v1`, and `terrarium.spatial.v1` remain intact.

The six existing objects now map to four small archetypes:

- **rolling:** `blue_stone`, `acorn`;
- **soft_nesting:** `red_thread`;
- **delicate:** `amber_leaf`;
- **keepsake:** `shell`, `glass_star`.

This is deliberately compact. 8D does not add a generic planner, needs/personality meters, inventory UI, quest logic, or an LLM action selector.

## Persistent state and later possibilities

Rolling objects use `settled → rolled → settled`. A supported nudge becomes a **roll**, and while rolled the object cannot simply be rolled again. Moss must re-engage it; the next same-object inspection becomes **retrieve** and restores `settled`.

The soft nesting object uses `loose → rumpled → nested`. On compatible floor/bed zones, nudge becomes **tug**, which produces `rumpled`; `rumpled` removes repeat tug and unlocks **nest**; loaf-on-object converts it to `nested`. Carrying it later restores a portable `loose` state. Tug/nesting is restricted to `open_space` and `sleeping_nook`, preventing implausible shelf/window/desk nests.

Delicate and keepsake objects expose inspect/carry rather than generic play/nudge. Keepsakes can enter `displayed` when placed on the collection shelf. The delicate leaf can return to `fresh` at the window or remain `handled` elsewhere. These are authoritative world facts, not renderer-only labels.

Every object carries additive identity fields, an interaction-state transition counter, and currently available affordances. Existing worlds are normalized conservatively: old possessions/coordinates/history remain and missing 8D identity state is added without fabricating prior transitions.

## Object-aware arrangement without overriding habits

Identity now nudges plausible arrangement destinations: rolling objects prefer open floor, soft objects favor bed/open floor, keepsakes favor the collection shelf, and the leaf favors the window. These are **tendencies**, not commands. The existing learned habit profile still influences choices and retains exploration/anti-lock-in behavior.

One important evaluator correction came from this change: an old controlled habit experiment changed both favorite zone *and* favorite object between its two worlds. That was no longer a valid isolated test once leaf/acorn identity genuinely affected outcomes. The zone-history probe now holds object identity constant; learned-object causality remains tested separately. All four long-horizon habit seeds pass the original causal thresholds.

## Causal session fixes found during UAT

8D implementation exposed two real state-machine defects and both were fixed before acceptance:

1. inspecting a rumpled thread could overwrite the unlocked nest intent, turning the follow-up into an ordinary loaf; rumpled inspection now preserves the object-session stage;
2. completed retrieve/nest sessions could remain open through repeated rest commitments; the first normal settle closes the completed object session.

The coherence evaluator was also corrected to measure its stated defect—rapid ordinary **A→B→A** travel—without counting meaningful object-delivery/event travel or long local sessions as if they were adjacent ping-pong. The rejection threshold itself was not weakened.

The Iteration-6 repertoire evaluator previously required at least four different nudgeable objects. 8D deliberately makes exactly three objects nudgeable (`blue_stone`, `acorn`, `red_thread`), so that gate now checks the intended consequence breadth against the new canonical affordance graph rather than requiring an illegal fourth play object.

## Authored object states

`display/art/objects/` contains **13 deterministic authored object-state assets** on the existing `terrarium.pixel-asset.v1` pipeline. The manifest now contains **73 assets total: 46 Moss + 13 object-state assets + existing room/static art**.

The renderer no longer reconstructs the six movable objects from per-kind rectangle recipes. Canonical object identity/state selects an authored variant, and placement/roll interpolation merely stages that asset at authoritative coordinates. Existing carried-object attachment and scene-layer contracts remain intact.

Authored states cover:

- blue stone: settled / rolled;
- acorn: settled / rolled;
- red thread: loose / rumpled / nested;
- amber leaf: fresh / handled;
- shell: handled / displayed;
- glass star: handled / displayed.

## Long-run object-affordance evidence

The dedicated four-seed 10,080-step evaluator passes on seeds `1701 / 1702 / 42 / 999`.

- roll→retrieve within two decisions: **96.15–100%**;
- tug→nest within two decisions: **85.71–100%**;
- illegal delicate/keepsake nudges: **0 on every seed**;
- roll counts: **14 / 23 / 26 / 20**;
- tug counts: **7 / 6 / 7 / 5**;
- displayed placements: **14 / 18 / 20 / 19**;
- all four archetypes are exercised and every object accumulates persistent state transitions.

Controlled-state checks also prove that a rolled object blocks repeat roll, a rumpled thread unlocks nest, and rolling/delicate objects expose different affordance subsets.

## Browser / temporal UAT

Final UAT used isolated `/tmp/terrarium-iteration8d-final`; canonical Moss/runtime was never reset or used as a fixture.

The final production-browser cross-regression includes the new roll/retrieve/tug/nest/display states plus accepted environment, left/right walk, carried walk, sleep/wake, sunlight, and thunder scenarios.

Key results:

- deterministic day sequence repeated **exactly**, raster-for-raster;
- every captured sequence preserved exact 400×240 → 800×480 2× nearest-neighbor output with **0 scale-error blocks**;
- roll: **11 samples / 6 distinct rasters**;
- retrieve: **11 / 5**;
- tug: **11 / 6**;
- nest: **11 / 7**;
- display: **11 / 7**;
- left walk: **11 / 8**; right walk: **11 / 7**; carried walk: **11 / 7**;
- sleep transition: **11 / 8**; waking: **11 / 6**;
- sunlight: **11 / 8**; thunder: **11 / 10**;
- continuity probe: **0 px** jump;
- RAF: **109 frames / 1800 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero intervals above 34 ms or 50 ms;
- browser console errors: **0**; the same benign temporal-fixture warning seen in prior accepted checkpoints remains.

The accepted object chain is visibly and semantically specific: acorn `settled → rolled → retrieved/settled`, red thread `loose → rumpled → nested` in open floor space, and shell `handled → displayed` on the collection shelf.

## Full validation

- pytest: **49/49 PASS**;
- Python-3.10 grammar: **36 sources PASS**;
- JavaScript syntax: **PASS**;
- authored asset/schema/bounds validation: **73/73 PASS**;
- technical evaluator at 10,080 events: **PASS** for append-only SQLite, hash chain, JSONL parity, restart, semantic frame contract, and exact snapshot+event replay;
- behavior, spatial, coherence, and habits: seeds **1701 / 1702 / 42 / 999**, 10,080 steps each: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational-event regression: **PASS**;
- Iteration-8D object-affordance evaluator: **PASS**;
- deterministic production-browser UAT: **PASS**;
- combined Iteration-8D regression matrix: **PASS**.

A managed heavy-job attempt at the 10,080-step technical evaluator exhausted that job container's temporary disk because the validation ledger is roughly 33.4 MB SQLite + 16.4 MB JSONL. The exact same evaluator was rerun in the normal project sandbox and passed. This was an evaluator-container capacity boundary, not a Terrarium persistence failure.

## Accepted checkpoint hashes

- snapshot: `20260828T112207258140Z-pixel-art-overhaul-iteration8d`;
- semantic frame: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`;
- renderer JS: `f8e12181a18c2616fdeb8dae1ee5a0453fab6ba3a5ab88912782e497e35cb701`;
- authored art: `ed1fee4cd060519267d131837ab45772754108c1c2eaa4c9a9c65322bce08d9a`;
- engine: `5a9b66bb020490b86cef9d3da6b0d538b3f457d65aa558c7bab824a65d4eb0be`;
- frame contract: `4811664e040a06219b887ca24abe4920982cb34536340e9e29b697301edf4bde`.

Unlike 8A–8C, the semantic frame hash **intentionally changes** because 8D adds authoritative object identity, interaction state, state-transition counts, and available-affordance projection.

## SBC / Gen18 decision

**Gen18: NO.**

The existing Terrarium state model, additive migration path, event ledger/replay, habit/session machinery, authored-art schema, deterministic fixtures, browser UAT, and evaluator tooling were sufficient. No reusable SBC substrate deficiency was found. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

## Next product iteration

**Iteration 8E — Atmospheric World.** Add quiet persistent non-commanding ambient life, richer exterior/window movement, deterministic placed local lighting, and stronger whole-scene weather mood while keeping that animation subordinate to Moss and outside behavior authority by default.
