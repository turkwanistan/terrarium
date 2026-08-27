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
