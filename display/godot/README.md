# Terrarium Godot vertical slice

This is a presentation-only Godot 4 proof of concept. Python/SQLite/event history remain canonical; this client consumes `terrarium.frame.v1` and does not write world state.

## Project-local tooling

Godot is intentionally not vendored. Use an installed Godot 4 binary (`godot4`/`godot`) or set `GODOT_BIN` when using `scripts/run_godot_slice.sh`.

## Deterministic fixture mode

```bash
python tools/build_godot_vertical_slice_fixtures.py
GODOT_BIN=/path/to/godot scripts/run_godot_slice.sh --fixture spring_clear_idle --manual-ms 1300
```

Deterministic off-screen capture requires a display-backed renderer. Godot's dummy `--headless` renderer does not expose a readable root viewport texture. Use a normal display session or Xvfb/Mesa, for example:

```bash
xvfb-run -a env LIBGL_ALWAYS_SOFTWARE=1 GODOT_BIN=/path/to/godot \
  scripts/run_godot_slice.sh --fixture winter_warm_night --manual-ms 1300 \
  --capture artifacts/godot-poc/winter-warm-night.png
```

The launcher intentionally rejects `--headless` together with `--capture` so future runs do not silently rediscover the dummy-renderer limitation.

Other useful fixtures are `spring_rain_idle`, `walk_to_window`, `inspect_red_thread`, `pickup_red_thread`, `carry_walk`, `red_thread_rumpled`, and `red_thread_nested`.

## Live read-only frame mode

```bash
GODOT_BIN=/path/to/godot scripts/run_godot_slice.sh --live --api-url http://127.0.0.1:8765
```

Live mode only performs `GET /api/frame`. Closing or reconnecting the renderer cannot advance, reset, or recreate canonical state.
