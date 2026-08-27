# Memory policy

Terrarium uses layered memory. The repository and live evidence are authority; memory is an index of reusable experience, never a replacement for evidence.

## Authority order

1. `terrarium.md`, source, tests, schemas, and explicit lifecycle decisions.
2. Persistent canonical world state/event history under the selected runtime data directory.
3. Reproducible evaluation and development-snapshot artifacts.
4. `history/` and `STATUS.md` for durable project decisions and failed approaches.
5. Self-Building Computer procedural memory for reusable procedures only.
6. Chat/session memory is convenience context only and must be revalidated against the repo.

## What belongs in memory

Record a reusable lesson only when it has a stable procedure and evidence. Prefer source/evaluator/content hashes over copied task bodies. Store applicability, preconditions, contraindications, failures, and authoritative references. Do not store high-churn world state, raw event ledgers, secrets, or subjective guesses as procedural memory.

A useful memory should answer: *when does this procedure apply, what authoritative capability/evaluator does it point to, and what evidence says it works?*

## Promotion discipline

Memory follows the same principle as Capability Forge: repeated evidence before trust. A candidate memory is discoverable for inspection but should not drive work as accepted procedure until held-out/reuse evidence qualifies it.

Gen17 imported the two successful real-task uses of promoted capability `simulation-behavior-auditor-r1` (`932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`) into procedural memory. Distillation produced candidate memory `315b9f1b2e40cfe5f2013e27463e170cfa90d90a6eeb0a272c46ac5f3f0c9e95`: two successes are enough to retain a hypothesis, but not enough for the distiller's held-out ACTIVE gate. Leave it CANDIDATE until future genuine reuse supplies qualifying evidence.

## Fresh-session retrieval

After reading authoritative project state, search procedural memory for the current task. Apply a retrieved memory only when its applicability/preconditions match and its capability/evaluator hashes still resolve. If memory disagrees with repository or live evidence, repository/live evidence wins. Record the result of genuine reuse so memory improves from actual work rather than prompt repetition.

## Gen17 retrieval check
The candidate behavior-auditor memory was queried with its exact task kind, applicability tags, runtime, input-schema hash, and required input keys. Retrieval returned the candidate at score `1.0` with no mismatches and authoritative capability/evaluator hashes intact. This validates discoverability without changing its state: it remains `CANDIDATE`, as intended.

## Runtime compatibility regression

The canonical always-on OptiPlex Terrarium runtime is currently Python 3.10. Project source must remain Python-3.10-syntax compatible until that host runtime is deliberately upgraded. `tests/test_python_compat.py` parses every project Python source using the Python 3.10 grammar so a newer development sandbox cannot silently introduce newer-only syntax.

## Runtime ownership regression

The persistent Terrarium database must be owned by the account that runs the world service. Mediated development services may create repo-local files as another UID, so Linux launchers must not depend on repository file ownership for the living database. They default to `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` and migrate legacy repo-local state with a verified SQLite backup. Source control stores product history; the user-owned runtime directory stores Moss's living state.

## Post-Gen17 lived-in-staging reuse

During the `2026-08-27-lived-in-staging` product checkpoint, the authoritative promoted capability `simulation-behavior-auditor-r1` was resolved again at content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f` with evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae` and reused on a genuine post-change 180-event Terrarium stream. The capability passed with sequence integrity, all 10 action classes, entropy `3.174454`, and 42 configured object interactions.

That successful real reuse was recorded as procedural episode `ep_091c8bfcdd8027f0ba2c`. Re-distillation produced memory object `3eaa33c60f47c1d4c2255ae518fdb573f111f10e8f389f045dcf050c39a1eed8`, but the held-out activation check remained fail-closed: the recorded episode's environment omitted the required `input_schema_hash` precondition, so applicability rejected it and the new memory remains `CANDIDATE`.

Do not reinterpret the successful capability run as an ACTIVE memory promotion. Do not weaken or delete the input-schema precondition to make the distiller pass. The episode is useful evidence, while repository/source/live state and the promoted Forge capability remain the authority.

## Post-Gen17 activity-aftermath reuse

For checkpoint `2026-08-27-activity-aftermath`, the promoted `simulation-behavior-auditor-r1` capability was reused on a fresh 180-event post-change stream and passed with all 10 action classes, entropy `3.174454`, 42 object interactions, and sequence integrity (`cap_20260827T054348Z_b67454cd`). Procedural-memory retrieval still returned `NO_MEMORY`; candidate memories remain non-authoritative. No gate was weakened and no new reusable SBC capability gap was justified.

## Post-Gen17 temporal-aftermath polish reuse

For checkpoint `2026-08-27-temporal-aftermath-polish`, the promoted `simulation-behavior-auditor-r1` capability was resolved at content hash `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f` with evaluator hash `1c9eaed4c4174212f84a7db52d4c5f47e1a106a88461f6880023d4dd7c5f53ae` and reused as a renderer-only behavior regression. The current deterministic 180-event stream SHA256 `fa438bef63e3aa56b353638b27b42248c06682347d4b8684cca3fc2874df5b11` matched the held-out audit vector exactly; Forge run `cap_20260827T115050Z_933e3d93` passed with all 10 action classes, entropy `3.174454`, 42 object interactions, and sequence integrity.

No new capability was forged because the iteration exposed no reusable capability gap. Existing procedural memories remain `CANDIDATE`/non-authoritative; no activation or promotion gate was weakened.

## Post-Gen17 temporal-rendering intelligence

For checkpoint `2026-08-27-temporal-rendering-intelligence`, Terrarium exposed a genuine reusable objective temporal-rendering gap. The accepted Forge path produced and explicitly promoted `temporal-render-auditor-r1`, content hash `5481ecd6e2e46d9b3a502fbabff5a24f27ffed9f925ab0868ed30a3ba13575b1`, evaluator hash `86b714f3871132ad3786f94fc81570dd569cb95ee09ced1d064737b5652a3b0c`.

The capability passed 6/6 independent Forge evaluation cases and 6/6 genuine Terrarium pre-promotion tasks (left/right walk, carried movement, idle control, rain control, and real RAF pacing). Gen14 Evaluator Mutation Nursery killed 10/10 dangerous mutants with zero survivors and accepted state unchanged. The capability uses only the Python standard library; no permanent MCP growth or SBC substrate change was required.

Objective temporal correctness is now authoritative through the promoted capability, but subjective warmth/charm/artistic quality remains outside its scope. Do not reinterpret pixel/trajectory metrics as an aesthetic oracle. Repository/source/live evidence remains higher authority than procedural memory, and existing candidate procedural memories remain non-authoritative unless their existing activation gates pass.

## Post-Gen17 present-world causality reuse

For checkpoint `2026-08-27-present-world-causality`, the promoted `temporal-render-auditor-r1` was reused against ten current deterministic Canvas scenarios plus real RAF pacing. All current scenarios and RAF passed; sampled movement retained zero reversals/facing mismatches, carried attachment span 0, and endpoint speed ratio `0.034956`. The promoted auditor remains an objective temporal-correctness tool only; it is not an artistic-quality oracle.

The checkpoint separately retained deterministic semantic-contact telemetry for the new present↔history interactions: sleeping-nook, window, and activity-corner engagement each rose monotonically from 0 to 1; representative red-thread placement settled from `(118,372)` to `(181,400)` with monotonic progress and zero final target error. These checks remain repository evidence rather than new permanent SBC capabilities.

The promoted `simulation-behavior-auditor-r1` was independently reused on a checksummed deterministic 80-event slice and returned sequence integrity, 10 action classes, entropy `3.095341`, and 21 configured object interactions. The native 500-step behavior evaluator remained unchanged at entropy `3.151553` with the inherited action/object distribution.

No new reusable capability gap was exposed, no new capability was forged, no activation gate was weakened, and no Gen18 substrate change is warranted. Existing candidate procedural memories remain non-authoritative.
## Post-Gen17 visual-maturity lessons

Checkpoint `2026-08-27-visual-maturity` established three reusable project lessons with direct evidence.

**Rendered-position continuity:** when a new canonical frame arrives while the disposable renderer is still interpolating the previous transition, presentation must begin the next interpolation from the creature's *currently rendered* position, not blindly from the prior canonical endpoint. The deterministic consecutive-update probe measured `352.907594 px` of instantaneous legacy discontinuity and `0 px` after rendered-position rebasing. This is a renderer continuity rule only; canonical state remains authoritative.

**Semantic-family suppression can improve presentation without scripting behavior:** treating `walk`/`explore` as one recent-action family and `carry`/`place` as another reduced seed-1701/500 consecutive movement pairs `50 → 19`, immediate zone reversals `9 → 5`, max movement burst `4 → 2`, and max manipulation burst `4 → 3`, while retaining all 10 action classes, 6 moved objects, and entropy `3.103385`. Any future change of this kind must compare before/after distributions and use the promoted behavior auditor; do not hide behavior changes in JavaScript.

**Temporal correctness is not aesthetic authority:** `temporal-render-auditor-r1` independently passed 15 deterministic real-Canvas sequences plus RAF pacing (16/16), proving trajectory/facing/attachment/settling/scene-stability correctness. `ART_DIRECTION.md` and human inspection of the actual 800×480 Canvas govern charm, warmth, composition, focal hierarchy, and material consistency. Do not add a synthetic beauty score merely to automate a subjective judgment.

Existing promoted capabilities were sufficient; no new capability was forged, no permanent MCP surface grew, and **No Gen18 warranted**.

## Post-Gen17 action-choreography-pacing lessons

Checkpoint `2026-08-27-action-choreography-pacing` established a reusable **multi-scale pacing rule**: a simulation heartbeat is not the same thing as a new behavioral decision, an action is not the same duration as its renderer interpolation, and environmental time must not advance at the same apparent rate as character acting. The accepted defaults are a three-real-second heartbeat, deterministic multi-tick behavior commitments, and one world minute per heartbeat. At seed 1701 / 500 heartbeats this produced 186 new decisions + 314 continuation ticks while retaining all 10 action classes and decision entropy `3.165646`. A full Terrarium day is now 72 real minutes rather than 9; deterministic weather blocks are about 9 real minutes. Future pacing changes must preserve these separate moment/action/behavior/environment scales unless new evidence justifies a deliberate change.

**Target ownership stays canonical:** interaction staging may use renderer posture, gaze, reach and interpolation, but the target object/destination must come from authoritative frame/event state. Renderer-owned target selection would create a second behavior authority. The accepted interaction pattern is bounded near-target stance → orientation/gaze → contact → hold/transfer/release → settle/recovery.

**Continuation ticks are not repeated decisions:** behavior-distribution auditing should distinguish canonical decisions from deterministic hold/settle continuation events. The native evaluator may inspect the full 500-heartbeat timeline, while `simulation-behavior-auditor-r1` can be fed the ordered decision subset with a derived contiguous audit sequence and preserved canonical sequence provenance. This prevents deliberate action holds from being misclassified as repetitive resampling.

**Use the temporal auditor as a rejection gate, not a ceremony:** the first post-change `temporal-render-auditor-r1` run rejected pickup/place endpoint settling at `0.104904` and sleep facing/settling. Acceptance was withheld, the locomotion endpoint curve and authoritative sleep facing were corrected, fresh Canvas evidence was captured, and the next run passed: pickup/place `0.04986`, sleep `0.095074` with zero facing mismatches, carried attachment span 0, RAF max 16.8 ms with zero stalls. This is the intended value of the promoted capability.

**Environmental interpolation does not create environmental authority:** the renderer may blend palette/daylight/night-glow between authoritative `world_minutes`, but canonical `world_minutes`, lighting phase and deterministic weather remain host-owned. Real-clock synchronization remains a possible future product choice, not an implicit renderer behavior.

The existing promoted behavior and temporal capabilities were sufficient; no capability was forged, no permanent MCP surface grew, and **No Gen18 warranted**.

## Post-Gen17 pixel-grid temporal specialization

Checkpoint `2026-08-27-pixel-art-overhaul-iteration1` established a reusable temporal-evaluation rule for integer-grid renderers. A valid pixel renderer can preserve a smooth deterministic presentation trajectory internally while snapping visible output to an integer art grid; short moves may therefore have an irreducible visible step large enough to trip a subpixel endpoint-speed ratio even when settling is correct.

Do not solve this by weakening the original dangerous defect gates or by pretending the quantized coordinate is smooth. The accepted reusable specialization is `grid-quantized-temporal-render-auditor-r1`, content hash `57fe2065ca3cc984241bee2da545db3bb318fd8a07ae90402a1dd6bc9993e697`, Forge evaluator hash `3115517877e016d4b4867da15b3d5ef81045991d3bf890765c53dfdaa9a6782f`. It may use the deterministic continuous presentation anchor for endpoint-settling measurement only when the visible coordinate remains within half a declared grid cell of that anchor; otherwise `grid_quantization_contract` fails closed. The original temporal oracle remained 10/10, Forge evaluation passed 6/6, two real tasks passed, and Gen14 killed 2/2 dangerous specialization mutants.

This is a capability specialization, not an SBC substrate deficiency. Existing Forge/Gen14 mechanisms handled it; **No Gen18 warranted**.
