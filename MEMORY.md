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
