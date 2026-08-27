# Present-world causality — 2026-08-27

This is a normal post-Gen17 Terrarium product checkpoint, not Generation 18.

## Goal

Make Moss's present activity feel physically connected to the habitat history already visible on screen, while preserving deterministic host-owned state, the 800×480 semantic frame contract, exact replay, and the disposable Canvas renderer.

## Defects found

The inherited renderer drew accumulated aftermath as passive background history: current activity did not visibly engage bedding, window traces, or the activity-corner surface. Temporal evidence also exposed two concrete spatial/transition defects:

- the canonical `window` contact anchor was `(168,132)`, placing Moss inside the glass while the sill-side object slots and wear contact region are around y≈263–281;
- placed carried objects snapped directly from Moss to the authored slot instead of visibly settling there.

## Bounded implementation

The canonical window contact anchor is now `(168,277)`. This fixes physical staging without changing action selection or world authority.

The renderer adds deterministic, presentation-only semantic engagement envelopes for three existing activities:

- `sleep` in `sleeping_nook` compresses/engages the accumulated bedding and gains a foreground blanket/contact layer;
- `look_outside` at `window` activates the existing pane/sill contact area;
- `inspect` / `carry` / `place` in `activity_corner` subtly engage the existing work surface/papers.

The envelope rises with deterministic renderer time and settles at 1.0; it does not write canonical state.

Object placement now renders a 900 ms smootherstep settle from Moss's carried position to the canonical authored destination. Canonical placement still occurs in the simulation/event ledger; this is only visual interpolation of the already-authoritative source→target transition.

Snapshot SVG thumbnails mirror settled semantic-contact cues so Git-friendly checkpoints remain representative of the real renderer without creating a second state model.

## Temporal evidence

Deterministic fixture coverage expanded to ten scenarios:

- left walk
- right walk
- carried walk
- arrive/settle
- object placement
- sleeping-nook activity
- window activity
- activity-corner activity
- idle control
- rain control

All were exercised through the actual 800×480 Canvas renderer with development-only exact timestamps. Repeated raw `left_walk` capture was byte-identical at SHA256 `518b7909af6c5c20e2573ee12f30923ca15faff4a1153954098137019c0d3a8a`.

The promoted `temporal-render-auditor-r1` (content `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`) passed all ten current deterministic scenarios plus the real-RAF probe. Movement metrics remained clean: zero facing mismatches/reversals, carried attachment span 0, endpoint speed ratio 0.034956 on the sampled moving scenarios. RAF evidence contained 109 intervals, max 16.8 ms, zero >50 ms stalls.

The promoted auditor does not claim to judge the new artistic causality envelopes or object-placement semantics directly. Those additions have separate deterministic checks from the captured telemetry:

- sleep engagement: monotonic `0 → 1`;
- window engagement: monotonic `0 → 1`;
- activity-corner engagement: monotonic `0 → 1`;
- red-thread placement: `(118,372) → (181,400)`, monotonic progress `[0, 0.011533, 0.134951, 0.603313, 0.964506, 1, 1, 1, 1, 1]`, final target error 0.

Larger raw browser captures were discarded after compaction. Bounded evidence is retained under `artifacts/causal-temporal-compact/`.

## Behavior / architecture regression

- pytest: **18/18 PASS**
- JavaScript syntax: **PASS**
- Python 3.10 syntax compatibility: **PASS**
- technical evaluator: **PASS**
- exact replay: **PASS**; canonical/replayed state hash `a7702ee51b4cb295cfb93b90ff295fcad38a31fc789a527609ea2f23606094c6`
- behavior evaluator seed 1701 / 500: **PASS**
- action entropy: **3.151553 bits**, unchanged
- 500-step action counts/object metrics: unchanged from the inherited temporal-rendering checkpoint

The existing promoted `simulation-behavior-auditor-r1` was independently reused on a checksummed deterministic 80-event slice: sequence integrity PASS, 10 action classes, entropy 3.095341 bits, 21 configured object interactions.

## Snapshot

Exactly one meaningful development snapshot was created:

- `20260827T142112545745Z-present-world-causality`
- seed 1701 / tick 97
- frame SHA256 `90a1cbd808506362a9d43a21ba3a97cd09036bcfe6a5c8220e47582c5404849c`
- renderer SHA256 `acf6dc6c5a08aed52f22810b951a3b797868d431546ee8cf632d41ba73c9472a`

Tick 97 intentionally shows Moss inspecting in the activity corner with accumulated history and no carried object, making this checkpoint's present↔history contact visible rather than storing a neutral comparison frame.

## SBC conclusion

No reusable Self-Building Computer substrate deficiency was exposed. Existing mediated Canvas capture, compact evidence transport, isolated Lab execution, the promoted temporal auditor, and the promoted behavior auditor were sufficient. Frozen Optiplex_MCP was not modified. No capability was forged and no Gen18 proposal is warranted.

## Runtime boundary

The canonical user-owned living database remains outside the mediated project sandbox and is not rewritten by this checkpoint. Development service verification may run the current source through Optiplex_MCP, but that must not be confused with canonical Moss state or claimed as a canonical LAN deployment unless an actual host-owned runtime update is independently verified.
