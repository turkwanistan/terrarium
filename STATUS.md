# Terrarium status

Terrarium is normal product development after the accepted Generation 17 pilot. This checkpoint is **not Generation 18**.

## Current checkpoint

Latest product checkpoint: **Visual maturity: art direction + motion coherence** (`history/2026-08-27-visual-maturity.md`).

Meaningful snapshot: `20260827T165449319827Z-visual-maturity` — seed **1701**, tick **180**; frame SHA256 `9a422b0de25ffa7311a1b86e315379189ae485485edc79bc02e948d0959a1487`; renderer SHA256 `a523186cab91e614034eb6593e3ea3db4b558ac448ca5d1c640cd43fb7362807`.

Primary evidence: `artifacts/visual-maturity.json`, `artifacts/visual-maturity-technical.json`, `artifacts/visual-maturity-behavior.json`, compact genuine Canvas evidence under `artifacts/visual-maturity-compact/`, and deterministic fixtures in `artifacts/temporal-render-fixtures.json`.

Inherited guarantees remain intact: host-owned canonical world state; deterministic seeded simulation; append-only/hash-chained event history; immutable snapshots + exact subsequent-event replay; disposable renderer; fixed hardware-neutral 800×480 `TerrariumFrame`; persistent objects/habitat wear/aftermath; canonical living state outside Git.

## Art direction / presentation

`ART_DIRECTION.md` now governs the reference renderer as a **cozy low-resolution storybook diorama**. Moss is the primary focal element; bedding/papers/local reactions are secondary; rain/light/motes are ambient and must not compete with Moss. Materials, palette, shape language, depth/contact, and motion grammar are explicitly defined.

Accepted presentation changes include:

- stronger Moss silhouette, proportions, grounding, carry posture, sleep curl, and restrained breathing/walk motion;
- distance-aware locomotion with anticipation/travel/settle/recovery rather than one generic transition;
- target-aware inspect/contact posing;
- staged pickup → attachment → carried locomotion → lower/contact/release/settle;
- live canonical-frame transitions rebased from Moss's exact currently rendered position;
- unified wood/cloth/paper/foliage/floor material language with quieter structural depth/contact shadows;
- reduced rain/mote density and contrast;
- normal world cadence restored to 3 seconds instead of launcher-forced 1 second.

The renderer remains non-authoritative and contains no second behavior engine.

## Objective motion evidence

The promoted `temporal-render-auditor-r1` remains authoritative for objective temporal correctness:

- content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`;
- evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`.

Independent isolated-Lab reuse: **15 deterministic real-Canvas hero sequences + real RAF = 16/16 PASS**. Sampled traversals have final progress 1.0, zero reversals/facing mismatches, endpoint-speed ratios `0.016818–0.037951`, and carried attachment span 0. RAF: 156 intervals, median 16.7 ms, max 16.8 ms, zero >50 ms stalls.

A dedicated consecutive-update continuity probe proves the fixed live defect: **352.907594 px legacy instantaneous jump → 0 px accepted jump**. Repeated raw deterministic `left_walk` capture is byte-identical at SHA256 `8853ad450bb5cac36ea5273b24de069b8ec9656ede77d7787574d1b7063992d5`.

These metrics are not a beauty score. Human inspection of the real 800×480 Canvas is the authority for charm, composition, warmth, and art-direction consistency.

## Behavioral presentation regression

One bounded authoritative simulation change groups recent-action suppression into semantic movement (`walk`/`explore`) and manipulation (`carry`/`place`) families so alternating actions cannot evade cooldowns and look indecisive.

Seed 1701 / 500 before → after:

- action classes: **10 → 10**;
- entropy: **3.151553 → 3.103385 bits**;
- consecutive movement pairs: **50 → 19**;
- immediate zone reversals: **9 → 5**;
- max movement burst: **4 → 2**;
- adjacent manipulation pairs: **10 → 7**;
- max manipulation burst: **4 → 3**;
- moved objects: **6 → 6**.

Current object interactions remain substantial: 53 inspections, 22 pickups, 22 placements. The promoted `simulation-behavior-auditor-r1` independently passed the fresh 500-event stream with sequence integrity, 10 action classes, entropy `3.103385`, and 97 configured object interactions.

## Regression

- pytest: **18/18 PASS**;
- JavaScript syntax: **PASS**;
- Python 3.10 syntax compatibility: **PASS**;
- technical evaluator: **PASS**;
- exact replay: **PASS**, canonical/replayed hash `5d3503fac94f66642ed338045a9f9ee15db83fbae47fcee29c94995067691fd0`;
- behavior evaluator seed 1701 / 500: **PASS**;
- deterministic repeat capture: **PASS**;
- real RAF pacing: **PASS**;
- promoted temporal auditor: **PASS**;
- promoted behavior auditor: **PASS**.

## SBC conclusion

Existing accepted SBC mechanisms were sufficient. No new capability was forged, no permanent MCP surface was added, and frozen Optiplex_MCP was not modified. **No Gen18 warranted.**

## Runtime / remote safety

Canonical Moss state lives outside Git in the user-owned runtime directory. Development evaluation used disposable temporary state and did not touch the canonical database. `origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use only the mediated project-safe Git push path and never copy credentials into the repository.

A development service or snapshot view is not a canonical LAN deployment. Report a deployment URL only after the actual host-owned runtime has been independently verified from the available safe boundary.

## Highest-value next product work

Use the art bible and hero reel as guardrails while deepening only a few high-value authored interactions or environmental compositions at a time. Prefer stronger contact/recovery and scene storytelling over more effects or more action types; preserve the same simulation/renderer authority boundary.
