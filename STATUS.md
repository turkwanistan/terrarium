# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. The current product checkpoint is **Pixel-Art Overhaul — Iteration 8D: Object Identity and Stateful Affordances**. This is **not Generation 18**.

## Current checkpoint

- history: `history/2026-08-28-pixel-art-overhaul-iteration8d.md`
- acceptance: `artifacts/pixel-art-overhaul-iteration8d.json`
- regression matrix: `artifacts/pixel-art-overhaul-iteration8d-regression-matrix.json`
- browser UAT: `artifacts/pixel-art-overhaul-iteration8d-browser-uat.json`
- object-affordance evaluation: `artifacts/pixel-art-overhaul-iteration8d-object-affordances.json`
- art-direction matrix: `artifacts/iteration8d-art-direction-matrix.json`
- art-direction fixtures: `artifacts/iteration8d-art-direction-fixtures.json`
- accepted snapshot: `20260828T112207258140Z-pixel-art-overhaul-iteration8d`
- deterministic seed/tick: **1701 / 10080**
- semantic frame SHA256: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`
- renderer JS SHA256: `f8e12181a18c2616fdeb8dae1ee5a0453fab6ba3a5ab88912782e497e35cb701`
- authored-art tree SHA256: `ed1fee4cd060519267d131837ab45772754108c1c2eaa4c9a9c65322bce08d9a`
- authored assets: **73 total / 46 Moss / 13 object-state**
- behavior rules: `terrarium-rules-v7-object-identity`
- object affordances: `terrarium.object-affordances.v1`
- deterministic RNG stream: `terrarium-rules-v3-routine-coherence`
- situational events: `terrarium.situational-events.v1`
- habits: `terrarium.habits.v1`
- spatial schema: `terrarium.spatial.v1`

The semantic hash intentionally changes from accepted 8C because object archetype, interaction state, transition counts, and currently available affordances are now authoritative state projected into `terrarium.frame.v1`.

## What Iteration 8D changed

The six persistent movable objects no longer share one generic interaction graph. Four canonical archetypes now constrain behavior:

- rolling — blue stone / acorn;
- soft nesting — red thread;
- delicate — amber leaf;
- keepsake — shell / glass star.

Rolling objects support roll→retrieve stateful play. Red thread supports zone-valid tug→rumple→nest. Delicate and keepsake objects reject generic nudge/play; keepsakes can become displayed on the collection shelf. Carry/place normalize later state according to object identity and destination.

All 8D fields migrate additively. Existing worlds retain object position, possession, event ledger, behavior context, habit profile, affordance history, and prior movement counts; missing identity state is added without pretending old interactions occurred.

Object identity also shapes plausible arrangement destinations as a bounded tendency beneath learned habits: rolling objects favor floor space, soft objects bed/open space, keepsakes the shelf, and the leaf the window. Habit causal influence and anti-lock-in thresholds remain intact.

## Authored object-state art

The existing `terrarium.pixel-asset.v1` pipeline now includes **13 object-state assets** under `display/art/objects/`. `display/web/app.js` selects these variants from canonical state instead of procedurally drawing each movable object by kind.

States include settled/rolled stone and acorn, loose/rumpled/nested thread, fresh/handled leaf, and handled/displayed shell/star. Existing continuous placement/roll interpolation, carried attachment, room depth, Moss acting, and exact 2× presentation remain unchanged in authority.

## UAT defects fixed before acceptance

- rumpled-thread inspection now preserves the unlocked nest stage rather than erasing it;
- completed retrieve/nest object sessions close on normal settle instead of generating repeated-rest loops;
- soft-object tug/nesting is restricted to `open_space` / `sleeping_nook`, preventing shelf/window/desk nests;
- the coherence evaluator now counts actual rapid ordinary A→B→A travel rather than collapsing meaningful object/event trips into false ping-pong;
- the controlled habit zone probe now holds object identity constant because 8D makes object archetype a genuine causal variable;
- the Iteration-6 repertoire consequence gate recognizes the new canonical fact that exactly three objects are nudgeable instead of demanding an illegal fourth.

## Browser / temporal UAT

Final production-browser UAT used isolated `/tmp/terrarium-iteration8d-final`; canonical Moss was never reset or used as a fixture.

- deterministic day sequence: **exact repeat**;
- roll: **11 / 6 distinct rasters**; retrieve **11 / 5**; tug **11 / 6**; nest **11 / 7**; display **11 / 7**;
- left walk **11 / 8**; right walk **11 / 7**; carried walk **11 / 7**;
- sleep **11 / 8**; waking **11 / 6**; sunlight **11 / 8**; thunder **11 / 10**;
- every sampled sequence: **0 scale-error blocks**;
- continuity: **0 px** jump;
- RAF: **109 frames / 1800 ms**, p50/p95 **16.7 ms**, max **16.8 ms**, zero >34 ms / >50 ms intervals;
- browser console errors: **0**; same benign fixture warning as prior accepted temporal UAT.

The final object fixture chain is semantically explicit: acorn `settled→rolled→retrieve/settled`; red thread `loose→rumpled→nested` in open space; shell `handled→displayed` on the shelf.

## Validation

- pytest: **49/49 PASS**;
- Python-3.10 grammar: **36 sources PASS**;
- JavaScript syntax: **PASS**;
- authored assets: **73/73 PASS**;
- technical evaluator at 10,080 events / append-only chain / restart / exact replay: **PASS**;
- behavior, spatial, coherence, habits: seeds **1701 / 1702 / 42 / 999**, 10,080 steps each: **all PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- Iteration-8D object-affordance evaluator: **PASS**;
- deterministic production-browser UAT: **PASS**;
- combined Iteration-8D regression matrix: **PASS**.

Long-run object evidence: roll→retrieve is **96.15–100%**, tug→nest **85.71–100%**, illegal delicate/keepsake nudges **0**, and every object exercises persistent state transitions.

## SBC conclusion

The existing Terrarium state/migration model, bounded intent/session machinery, replay/event ledger, habit system, authored-art pipeline, deterministic fixtures, and browser/evaluation tools were sufficient. No reusable substrate deficiency was exposed. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

**Gen18: NO**

## Next: Iteration 8E — Atmospheric World

Make the accepted room feel alive even while Moss is still:

- add deterministic persistent non-commanding ambient motion separate from situational events;
- enrich exterior/window life, foliage, curtain/rain traces and other quiet environmental loops;
- add hard-edged placed local lighting where composition supports it;
- strengthen warm-interior/cool-exterior contrast and whole-scene weather mood;
- preserve Moss/object/event authority: ambient presentation normally must not become a behavior command.

Success means stillness can remain interesting without turning the habitat into a particle show or silently expanding Moss intelligence.

## Runtime / Git safety

Canonical Moss remains user-owned outside Git. Runtime databases/event ledgers remain ignored. Host deployment must preserve `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` (or explicit `TERRARIUM_DATA_DIR`) and must not substitute a disposable development world.
