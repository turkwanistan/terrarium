# Terrarium

Terrarium is a persistent artificial creature and habitat. The canonical creature, world, possessions, and event history live in the host-owned world process; the browser is a disposable 800×480 renderer that reconnects to authoritative state.

Gen17 implements the first product-building checkpoint from `terrarium.md`: Phase 0 contracts/state/replay, Phase 1 autonomous visible life, and Phase 2 persistent objects.

## Run

```bash
python -m terrarium.api.server --host 0.0.0.0 --port 8080 --data-dir data/live --seed 1701 --tick-seconds 1
```

Open `http://localhost:8080/`. Closing the browser does not stop the world process. Restarting the process against the same data directory resumes canonical state.

## See it yourself

On Windows, from the repository root:

```powershell
.\scripts\run_windows.ps1
```

This starts the persistent local world, opens `http://127.0.0.1:8080/`, and keeps canonical state under `data/live/`. The development snapshot gallery is at `http://127.0.0.1:8080/snapshots/`. On Linux/macOS use `./scripts/run_local.sh`.

## Progressive development snapshots

Snapshots are **development milestones**, not copies of the high-churn creature database. Capture a fixed deterministic comparison scene after a meaningful visible/product change:

```bash
python tools/capture_dev_snapshot.py cozy-object-storytelling-r1 --note "Objects and wear now tell a clearer story."
```

Each checkpoint stores a small `frame.json`, metadata, renderer/source hashes, and a note under `snapshots/dev/`. The gallery renders those frames through the real browser renderer. Git history preserves the exact renderer version associated with each checkpoint. Use deterministic seed `1701` / step `240` by default so visual evolution is comparable over time.

## Git history

The intended remote is `git@github.com:turkwanistan/terrarium.git`. Make one commit/push per meaningful, tested checkpoint rather than per tiny edit. A good checkpoint contains code + tests/evaluation + snapshot + concise status/history update. Runtime `data/live/` is deliberately excluded from Git.

See `MEMORY.md` for the evidence-backed memory policy.

## Evaluate

```bash
python -m pytest -q
python evaluations/evaluate_technical.py --out artifacts/gen17-technical-eval.json
python evaluations/evaluate_behavior.py --seed 1701 --steps 500 --out artifacts/gen17-behavior-eval.json
```

The technical evaluator proves fixed 800×480 framing, append-only/hash-chained events, restart persistence, semantic renderer frames, and exact snapshot+event replay. The behavior evaluator measures action diversity/repetition, object interactions, impossible carry states, object movement, and visible habitat accumulation.

## Architecture

- `terrarium/models.py` — canonical typed world/state contracts and deterministic constants.
- `terrarium/events.py` — versioned event records, compact state patches, hashes, chain verification.
- `terrarium/store.py` — SQLite canonical state, immutable snapshots, append-only event persistence, JSONL inspection ledger.
- `terrarium/engine.py` — deterministic seeded autonomous simulation.
- `terrarium/replay.py` — exact snapshot + subsequent-event reconstruction.
- `terrarium/frame.py` — hardware-neutral `terrarium.frame.v1` projection, exactly 800×480 logical pixels.
- `terrarium/api/server.py` — persistent world service and read-only browser-facing API.
- `display/web/` — reference Canvas diorama renderer; never authoritative.
- `evaluations/` — technical/behavior evaluators and Gen16 project capability pack.
- `artifacts/` — reproducible Gen17 evidence.

## Authority

`terrarium.md` is product/design intent. Source and tests define the implemented contracts. Generated artifacts are evidence, not authority over source. Live state under `data/live/` is runtime state and is intentionally not source control.

The eventual hardware fork must consume the same TerrariumFrame/state/history rather than creating a second creature.