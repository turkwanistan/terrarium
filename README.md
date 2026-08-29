# Terrarium

Terrarium is a persistent artificial creature and habitat. The canonical creature, world, possessions, and event history live in the host-owned world process; presentation is disposable and reconnects to authoritative state. The current presentation canary uses Godot by default, with the Canvas renderer retained as an explicit same-world fallback.

Gen17 implements the first product-building checkpoint from `terrarium.md`: Phase 0 contracts/state/replay, Phase 1 autonomous visible life, and Phase 2 persistent objects.

## Run

Keep world lifecycle and presentation lifecycle separate. On the persistent OptiPlex host, start or reuse the canonical world/API with:

```bash
./scripts/run_lan.sh
```

This owns the living `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` world. Closing or failing presentation never stops Moss.

The normal canary target is now **Godot in a browser**, not a native Godot install on every viewing PC. After the generated web payload is present, start the read-only HTTPS presentation gateway on the OptiPlex in a second terminal/service:

```bash
./scripts/run_presentation.sh
```

It prints a URL similar to:

```text
https://<terrarium-host>:8766/
```

Open that URL from the PC/browser you want to use. The viewing PC needs **no Godot installation, repository clone, WSL setup, or simulation process**. During the canary the gateway uses a local self-signed certificate, so the browser may require a one-time Advanced/Proceed confirmation.

The browser export is single-threaded and presentation-only. Its page origin is also its API origin; the HTTPS gateway serves generated Godot Web files and proxies only read-only `GET /api/frame` and `GET /api/health` to the existing canonical HTTP world service. It exposes no `/api/step`, POST/write route, database access, planner, migration, or world lifecycle operation.

Immediate Canvas rollback remains the existing world URL printed by `run_lan.sh`, or:

```bash
TERRARIUM_API_URL=http://127.0.0.1:8765 ./scripts/run_presentation.sh --canvas
```

Native Godot remains an explicit development/UAT option only:

```bash
TERRARIUM_API_URL=http://<terrarium-host>:<port> \
GODOT_BIN=/path/to/godot \
./scripts/run_presentation.sh --native
```

`run_local.sh` and `run_windows.ps1` remain legacy local Canvas development conveniences. `scripts/run_godot_live_candidate.sh` remains the bounded native-client path. `mcp-lab` remains isolated native-validation infrastructure only and must not become an always-on Xvfb/llvmpipe presentation host.

The Godot Web payload under `display/web/godot/` is generated from `display/godot_reference_v2/` by `.github/workflows/build-godot-web.yml`; normal presentation startup never regenerates art or compiles Godot.

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
- `display/web/` — browser presentation assets: Canvas fallback plus generated Godot Web payload; never authoritative.
- `tools/godot_web_gateway.py` — HTTPS static/read-only frame gateway for the Godot browser canary; never world authority.
- `display/art/` — validated text-addressable authored pixel assets, palettes, and manifest; presentation source only, never world authority.
- `tools/capture_art_direction_matrix.py` — deterministic production-renderer fixture matrix for visual comparison.
- `evaluations/` — technical/behavior evaluators and Gen16 project capability pack.
- `artifacts/` — reproducible Gen17 evidence.

## Authority

`terrarium.md` is product/design intent. Source and tests define the implemented contracts. Generated artifacts are evidence, not authority over source. Live runtime state is intentionally outside source control and, on Linux, outside the repository by default.

The eventual hardware fork must consume the same TerrariumFrame/state/history rather than creating a second creature.