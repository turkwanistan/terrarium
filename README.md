# Terrarium

Terrarium is a persistent artificial creature and habitat. The canonical creature, world, possessions, and event history live in the host-owned world process; the browser is a disposable 800×480 renderer that reconnects to authoritative state.

Gen17 implements the first product-building checkpoint from `terrarium.md`: Phase 0 contracts/state/replay, Phase 1 autonomous visible life, and Phase 2 persistent objects.

## Run

For normal host use, prefer the launch scripts rather than invoking the server with a repo-local database:

```bash
./scripts/run_local.sh
# or, for another device on the trusted LAN:
./scripts/run_lan.sh
```

Linux launchers store the living canonical world under `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` by default. On first launch they safely migrate any legacy repo-local `data/live` database using SQLite backup and verify that canonical state matches before starting. Closing the browser does not stop the world process. Restarting the process against the same runtime directory resumes canonical state.

## See it yourself

On Windows, from the repository root:

```powershell
.\scripts\run_windows.ps1
```

This starts the persistent local world and opens `http://127.0.0.1:8080/`. The development snapshot gallery is at `http://127.0.0.1:8080/snapshots/`. On Linux/macOS use `./scripts/run_local.sh`.

To keep the canonical world on the OptiPlex but view it from your PC on the same trusted LAN, run `./scripts/run_lan.sh` on the OptiPlex. It prints the LAN URL to open from your PC. This is intentionally unauthenticated and should not be exposed to the public internet.

## Progressive development snapshots

Snapshots are **development milestones**, not copies of the high-churn creature database. Capture a fixed deterministic comparison scene after a meaningful visible/product change:

```bash
python tools/capture_dev_snapshot.py cozy-object-storytelling-r1 --note "Objects and wear now tell a clearer story."
```

Each checkpoint stores a small `frame.json`, metadata, renderer/authored-art/source hashes, a GitHub-friendly `preview.svg`, and a note under `snapshots/dev/`. `snapshots/README.md` becomes the browsable visual timeline, while the local gallery renders those frames through the real browser renderer. Git history preserves the exact renderer version associated with each checkpoint. Use deterministic seed `1701` / step `240` by default so visual evolution is comparable over time.

## Git history

The intended remote is `git@github.com:turkwanistan/terrarium.git`. Make one commit/push per meaningful, tested checkpoint rather than per tiny edit. A good checkpoint contains code + tests/evaluation + snapshot + concise status/history update. Runtime world state is deliberately excluded from Git whether it lives in the XDG state directory or a custom `TERRARIUM_DATA_DIR`.

See `MEMORY.md` for the evidence-backed memory policy.

Visual direction is governed by `ART_DIRECTION.md`; the accepted Iteration-8A authored-art foundation lives under `display/art/`, and the next room-recomposition step is defined in `VISUAL_STYLE_OVERHAUL.md` / `ROADMAP.md`.

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
- `display/art/` — validated text-addressable authored pixel assets, palettes, and manifest; presentation source only, never world authority.
- `tools/capture_art_direction_matrix.py` — deterministic production-renderer fixture matrix for visual comparison.
- `evaluations/` — technical/behavior evaluators and Gen16 project capability pack.
- `artifacts/` — reproducible Gen17 evidence.

## Authority

`terrarium.md` is product/design intent. Source and tests define the implemented contracts. Generated artifacts are evidence, not authority over source. Live runtime state is intentionally outside source control and, on Linux, outside the repository by default.

The eventual hardware fork must consume the same TerrariumFrame/state/history rather than creating a second creature.