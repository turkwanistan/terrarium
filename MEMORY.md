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
