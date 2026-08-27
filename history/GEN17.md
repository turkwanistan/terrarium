# Gen17 — Stop Building the Factory; Use It

Date: 2026-08-27

Gen17 used Terrarium as the first full project-building pilot on the accepted Gen16 project factory.

## What was built
A new `/home/mcp/projects/projects/terrarium` repository implementing the initial Phase 0–2 Terrarium scope: deterministic world/state, append-only events, snapshots/replay, persistent autonomous creature, 800×480 reference renderer, multiple habitat zones, and persistent inspect/carry/place objects.

## Evidence-driven iterations
1. The first full-state-per-event representation was correct but grew to ~889 KB JSONL per 100 events. It was replaced with compact deterministic state patches and tick-addressable seeded entropy; the comparable footprint fell to ~124 KB while exact replay remained true.
2. Standalone evaluator entrypoints initially depended on pytest adding the project root to Python import resolution. Both evaluators were fixed to locate the project root themselves so fresh-session documented commands work.
3. Browser close/reopen proved the world advanced from tick 36 to 63 with no renderer. A new service process resumed persisted state and later reached tick 87 instead of resetting.

## Project-driven builder evolution
Gen16 analysis identified one genuine missing valuable reusable capability: simulation behavior auditing. `simulation-behavior-auditor-r1` was forged, evaluated 3/3, exercised successfully on two Terrarium streams, then promoted by the existing governor. Content hash: `932573954fdf126bd4ec4f4d5a1f79a50b48b994bf374ed0cfa3415120dd093f`.

A dangerous fail-open mutation that forced `sequence_ok` true was killed by the Gen14 nursery with an independent sequence-gap oracle; dangerous kill rate 1.0, no survivor, one physical isolation owner, accepted state unchanged.

Terrarium also exposed a real Lab dependency defect: Forge expected Draft-2020-12 JSON Schema support but live `jsonschema 3.2.0` lacked it. The guest-local dependency was repaired to pinned `jsonschema 4.23.0`; Forge selftest passed 8/8 and Gen16 benchmark passed 40/40 afterward. No permanent MCP tool was added and operational server/LKG remained unchanged.

## Final stopped live world evidence
`artifacts/gen17-live-replay.json` records 402 events/ticks with exact replay hash equality. The live service was stopped after browser acceptance so no temporary write-capable service remained.

No commit or push was performed.