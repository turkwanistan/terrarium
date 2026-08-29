# Terrarium

Terrarium is a persistent artificial creature and habitat. The canonical creature, world, possessions, and event history live in the host-owned world process; presentation is disposable and reconnects to authoritative state. The current presentation canary uses Godot by default, with the Canvas renderer retained as an explicit same-world fallback.

Gen17 implements the first product-building checkpoint from `terrarium.md`: Phase 0 contracts/state/replay, Phase 1 autonomous visible life, and Phase 2 persistent objects.

## Run

Keep world lifecycle and presentation lifecycle separate. On the persistent host, start or reuse the canonical world/API with:

```bash
./scripts/run_lan.sh
```

This owns the living `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` world. Closing or failing a presentation client does not stop Moss.

On a **graphical Linux/macOS client** with this repository and Godot 4 installed, Godot is now the normal presentation choice:

```bash
TERRARIUM_API_URL=http://<terrarium-host>:<port> \
GODOT_BIN=/path/to/godot \
./scripts/run_presentation.sh
```

Immediate Canvas rollback against the same world:

```bash
TERRARIUM_API_URL=http://<terrarium-host>:<port> ./scripts/run_presentation.sh --canvas
```

On a **graphical Windows client**:

```powershell
$env:TERRARIUM_API_URL = "http://<terrarium-host>:<port>"
$env:GODOT_BIN = "C:\path\to\Godot_v4.7.2-stable_win64.exe"
.\scripts\run_presentation.ps1
```

Canvas rollback on Windows:

```powershell
.\scripts\run_presentation.ps1 -Mode canvas -ApiUrl $env:TERRARIUM_API_URL
```

The selectors consume existing generated production art and require an already-running `GET /api/frame`. They do not start, step, migrate, reset, stop, or write the canonical world. Headless/Xvfb/llvmpipe is not the production presentation path; `mcp-lab` remains bounded native-validation infrastructure only.

`run_local.sh` and `run_windows.ps1` remain legacy local Canvas development conveniences; they are not the staged Godot cutover path. The trusted-LAN API is intentionally unauthenticated and must not be exposed to the public internet.

## Progressive development snapshots

Snapshots are **development milestones**, not copies of the high-churn creature database. Capture a fixed deterministic comparison scene after a meaningful visible/product change:

```bash
python tools/capture_dev_snapshot.py cozy-object-storytelling-r1 --note "Objects and wear now tell a clearer story."
```

Each checkpoint stores a small `frame.json`, metadata, renderer/authored-art/source hashes, a GitHub-friendly `preview.svg`, and a note under `snapshots/dev/`. `snapshots/README.md` becomes the browsable visual timeline, while the local gallery renders those frames through the real browser renderer. Git history preserves the exact renderer version associated with each checkpoint. Use deterministic seed `1701` / step `240` by default so visual evolution is comparable over time.

## Git history

The intended remote is `git@github.com:turkwanistan/terrarium.git`. Make one commit/push per meaningful, tested checkpoint rather than per tiny edit. A good checkpoint contains code + tests/evaluation + snapshot + concise status/history update. Runtime world state is deliberately excluded from Git whether it lives in the XDG state directory or a custom `TERRARIUM_DATA_DIR`.

See `MEMORY.md` for the evidence-backed memory policy.

Visual direction is governed by `ART_DIRECTION.md`; the accepted Iteration-8B room, Iteration-8C authored Moss vocabulary, Iteration-8D object-state variants, Iteration-8E atmosphere, and Iteration-8F seasonal world now live across `display/art/`, canonical frame/state contracts, and `display/web/app.js`. Iteration 8F adds canonical `terrarium.seasons.v1` state on a 21-real-day-per-season cadence, authored seasonal exterior/palette treatment, conservative existing-world migration, and neutral rendering when season authority is absent. The next product milestone is **Iteration 9 — Emergent Situations and Consequence Memory** in `ROADMAP.md`.

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