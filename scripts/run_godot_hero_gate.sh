#!/usr/bin/env bash
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PROJECT="$ROOT/display/godot_hero"
GODOT_BIN="${GODOT_BIN:-}"
if [ -z "$GODOT_BIN" ]; then
  if command -v godot4 >/dev/null 2>&1; then GODOT_BIN="$(command -v godot4)"
  elif command -v godot >/dev/null 2>&1; then GODOT_BIN="$(command -v godot)"
  else echo "Godot 4 not found. Set GODOT_BIN=/path/to/godot" >&2; exit 127
  fi
fi

# The art generator is deterministic, but rewritten PNGs need a Godot import pass
# before a fresh project can load them. Keep that setup local and bounded here.
python "$PROJECT/tools/generate_hero_art.py" >/dev/null
GODOT_SILENCE_ROOT_WARNING=1 "$GODOT_BIN" --headless --editor --path "$PROJECT" --quit >/dev/null
exec "$GODOT_BIN" --path "$PROJECT" -- "$@"
