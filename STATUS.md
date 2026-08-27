# Terrarium status

This is normal Terrarium development after the accepted Generation 17 pilot. It is **not Generation 18**.

## Current checkpoint

Latest product checkpoint: **Present-world causality** (`history/2026-08-27-present-world-causality.md`).

Meaningful snapshot: `20260827T142112545745Z-present-world-causality` — deterministic seed **1701**, tick **97**; frame SHA256 `90a1cbd808506362a9d43a21ba3a97cd09036bcfe6a5c8220e47582c5404849c`; renderer SHA256 `acf6dc6c5a08aed52f22810b951a3b797868d431546ee8cf632d41ba73c9472a`.

Primary evidence: `artifacts/present-world-causality.json`, `artifacts/present-world-causality-technical.json`, `artifacts/present-world-causality-behavior.json`, compact Canvas captures under `artifacts/causal-temporal-compact/`, and deterministic fixtures in `artifacts/temporal-render-fixtures.json`.

Inherited Gen17 guarantees remain intact: host-owned canonical world state; deterministic simulation; append-only/hash-chained history; immutable snapshots + exact replay; disposable renderer; fixed hardware-neutral 800×480 `TerrariumFrame`; persistent objects/habitat wear/aftermath; canonical living state outside Git.

## Product improvement

Present activity now visibly engages accumulated habitat history instead of floating independently of it:

- canonical window contact moved from `(168,132)` to `(168,277)`, aligning Moss with the sill-side authored contact region rather than inside the glass;
- sleeping in the nook deterministically engages/compresses existing bedding and gains a foreground contact layer;
- window watching activates the existing pane/sill contact area;
- inspect/carry/place in the activity corner subtly engages the existing work surface/papers;
- carried-object placement visually settles over 900 ms from Moss to the authoritative authored target instead of snapping.

These are renderer/contact improvements, not a second state model. The simulation/event ledger remains authoritative.

## Objective temporal evidence

Promoted `temporal-render-auditor-r1` remains authoritative for temporal correctness:

- content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`
- evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`

Current genuine Canvas evidence: **10/10 deterministic scenarios PASS plus real RAF PASS**. Sampled movement has zero reversals/facing mismatches, carried attachment span 0, endpoint speed ratio `0.034956`. RAF: 109 intervals, max `16.8 ms`, zero >50 ms stalls.

Repeated raw deterministic `left_walk` capture is byte-identical at SHA256 `518b7909af6c5c20e2573ee12f30923ca15faff4a1153954098137019c0d3a8a`.

The promoted auditor does **not** judge warmth/charm or directly score the new semantic-contact envelope. Separate deterministic telemetry proves sleep/window/activity-corner engagement rises monotonically `0 → 1`. Placement telemetry proves red thread `(118,372) → (181,400)` with monotonic settle progress and zero final target error.

## Regression

- pytest: **18/18 PASS**
- JavaScript syntax: **PASS**
- Python 3.10 syntax compatibility: **PASS**
- technical evaluator: **PASS**
- exact replay: **PASS**, canonical/replayed hash `a7702ee51b4cb295cfb93b90ff295fcad38a31fc789a527609ea2f23606094c6`
- behavior evaluator seed 1701 / 500: **PASS**
- action entropy: **3.151553 bits**, unchanged
- action counts/object metrics: unchanged from the inherited temporal-rendering checkpoint

Promoted `simulation-behavior-auditor-r1` was independently reused on a checksummed deterministic 80-event slice: sequence integrity PASS, 10 action classes, entropy `3.095341`, 21 configured object interactions.

## SBC conclusion

No reusable Self-Building Computer substrate deficiency was found. Existing mediated browser capture, bounded evidence transport, isolated Lab execution, `temporal-render-auditor-r1`, and `simulation-behavior-auditor-r1` were sufficient. No new capability was forged. Frozen Optiplex_MCP was not modified. **No Gen18 proposal is warranted.**

Candidate procedural memories remain non-authoritative unless their existing activation gates are met.

## Runtime / remote

Canonical living Moss state remains outside Git and outside the mediated development sandbox. The finished source was verified in a managed Optiplex_MCP development service at the exact 800×480 checkpoint view. That mediated service is not the canonical host-owned database and is not claimed as a canonical LAN deployment; the canonical user-owned runtime still requires independent host verification.

`origin` is `git@github.com:turkwanistan/terrarium.git`; `main` tracks `origin/main`. Use the mediated project push path; do not embed or copy credentials.

## Highest-value next product improvement

Deepen **local action staging and object affordances**: let Moss's existing inspect/carry/place/look/sleep activities use clearer anticipation, contact, and recovery staging around the specific nearby object/surface, while preserving current state authority and using temporal checks for correctness rather than aesthetics.
