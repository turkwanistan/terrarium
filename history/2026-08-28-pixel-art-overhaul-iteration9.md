# Pixel-Art Overhaul — Iteration 9: Emergent Situations and Consequence Memory

**Status: ACCEPTED — 2026-08-28**

Iteration 9 makes prior consequences matter later without adding a generic planner, quest system, needs/personality stats, dialogue, inventory UI, LLM action selector, or renderer-side behavioral memory.

## What changed

Terrarium now has canonical `terrarium.consequence-memory.v1`, a compact bounded index of unresolved causal consequences. The complete event ledger remains append-only history; the hot index is capped at **12** entries and only retains consequences still capable of becoming later opportunities. Entries expire after at most **4,320 simulated minutes** and cannot become eligible sooner than a bounded delay (45 minutes globally; longer delays are used by specific causes).

Consequences can be created by engaged/oriented situational aftermath, persistent path-wear traces, object arrangements, object displacement, and completed soft-object nests. Repeated equivalent causes merge/reinforce rather than growing the hot index without bound. Retention is deterministic and significance-aware so rare/strong unresolved causes are not blindly evicted by common arrangement churn.

When an eligible consequence wins the deterministic opportunity gate, the existing bounded intent/session machinery expresses the chain:

**prior cause → later recognition → ordinary approach → re-engagement → bounded recovery**

No new navigation planner exists. Recognition uses the existing `react` vocabulary, approach uses existing authored route authority, engagement reuses `inspect`, `loaf`, `rest`, or `look_outside`, and the commitment releases after one revisit.

## History sensitivity

The dedicated evaluator proves two worlds can have the same immediate visible frame while carrying different causal histories. They remain visually equal until a controlled recognition, then diverge deterministically at tick **627**. Each history is independently deterministic. Seasonal/weather context, learned zone affinity, arrangements, and comfort traces may modulate opportunity score, but they do not fabricate causes.

The migration path for pre-Iteration-9 worlds is deliberately neutral: `migration_origin=neutral-existing-world`, empty entries, zero counters. Old event history is not rescanned to invent consequences that supposedly happened before the feature existed. Objects and habits are unchanged by migration.

## Representative emergent chain

The deterministic production fixture found a real chain rather than scripting one:

- tick **1760**: Moss tugs the red thread; it becomes `rumpled`, creating an `object_displacement` consequence;
- tick **2932**: the same consequence (`con-8870385a3b6b6448`) becomes relevant while Moss is at the window; Moss pauses/reacts;
- tick **2936**: Moss follows the ordinary authored route from the window toward the sleeping nook;
- tick **2938**: Moss settles into a quiet loaf at the target area and the revisit resolves.

The source and revisit are separated by well over a thousand simulation ticks. Renderer telemetry carries the same authoritative memory ID/source through recognize/approach/engage, but the renderer stores no private consequence memory.

## Long-run evidence

Seeds **1701 / 1702 / 42 / 999**, each at **10,080 steps**, all pass. They produce **14–19** later revisits per seed, maximum causal-chain duration **6 ticks**, maximum open hot entries **12**, quiet-action share roughly **52–56%**, recognition below **0.7%** of decisions, and zero possession/object-state integrity violations. Recognition ages range from **286** to more than **4,000 simulated minutes**, proving the feature is genuinely delayed rather than an immediate follow-up mechanism.

The 10,080-event technical evaluator passes append-only integrity, restart, and exact replay. Canonical/replayed deterministic state SHA256 is `d611fa61d2a841323dad5288962f937d952e62920877b29ace85f33bbdeadb32`.

Regression-contract refinements were explicit rather than silent weakening: seasonal behavior must remain identical before any consequence is eligible but may later influence an authoritative stored opportunity; consequence `react` events are no longer misclassified as weather reactions; tug→nest is accepted as the correct soft-object causal follow-up; and the sunlight-authority test now uses the standard 10,080-step horizon because history sensitivity intentionally changes exact long-run timing.

## Browser / visual UAT

The production renderer required no new visual subsystem. Existing Moss poses and authored routing make the new causal chain readable:

- recognize: stationary `react`, pixel hash `fnv1a32:70f5e46d`;
- approach: in-flight authored route, pixel hash `fnv1a32:e8335ae5`;
- engage: stationary `loaf`, pixel hash `fnv1a32:39f30efd`.

All observed frames preserve exact 400×240 → 800×480 2× integer scaling with smoothing off. The chain contains no confounding world event and no renderer-only narrative marker. Human/vision review accepted the pause → purposeful cross-room return → quiet re-engagement as understandable with the existing visual vocabulary.

## Evaluation

- pytest: **60/60 PASS**;
- Python-3.10 grammar: **41 sources PASS**;
- JavaScript syntax: **PASS**;
- technical evaluator: **10,080 events / append-only / restart / exact replay PASS**;
- behavior/spatial/coherence/habits: seeds **1701 / 1702 / 42 / 999**, **10,080 steps each**, all PASS;
- repertoire / situations / object-affordances / atmosphere / seasons: **PASS**;
- dedicated consequence evaluator, four seeds × 10,080: **PASS**;
- deterministic history-sensitivity control: **PASS**;
- production-renderer consequence-chain UAT: **PASS**;
- combined Iteration-9 regression matrix: **PASS**.

Accepted deterministic snapshot: `20260828T182004989725Z-pixel-art-overhaul-iteration9`

- frame SHA256: `33cced839bb3c2067da01b786c705bf5e3a2a645086e4cfdabee3748ee93f17a`
- renderer SHA256: `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`
- authored-art SHA256: `cd2ec842e4661aa72e7a81ba7ac2504f0e1718319f75afa9bb8666efb942359e`

## Canonical deployment

The accepted code was restarted against the same user-owned `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` world. No runtime database/event ledger was deleted, copied, replaced, or reset.

Verified post-deploy:

- original world `created_at`: `2026-08-27T03:45:50.032660Z` preserved;
- tick / event count: **80,715 / 80,715**;
- rules: `terrarium-rules-v9-consequence-memory`;
- consequence schema: `terrarium.consequence-memory.v1`;
- consequence migration: `neutral-existing-world`;
- entries/counters at verification: empty / zero (no fabricated prior consequences);
- existing season epoch preserved: `2026-08-28T16:33:07.468419Z`;
- season/stage: `spring / early`;
- replay: **PASS**;
- canonical and replayed state SHA256: `e6e5c57d8c49444831a1b765f70e01c31221b9fba9a50138a60a2b344eeb76b3`.

## SBC / next step

No reusable substrate deficiency appeared. Existing Terrarium/Optiplex tooling was sufficient; Self-Building Computer and the frozen MCP surface were not modified. **Gen18: NO.**

Highest-impact next product direction: **Iteration 10 — Causal Composition and Situation Chaining**. Iteration 9 proves one stored cause can become a later bounded revisit. The next gain should come from allowing a *present* event/opportunity to intersect with an *existing* consequence/object state/habit so two or more current systems compose into richer unscripted situations. Do this with the same bounded authority model before considering more memory, more verbs, or a generic planner.
