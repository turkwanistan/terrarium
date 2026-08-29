#!/usr/bin/env bash
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -n "${GODOT_BIN:-}" ]; then
  GODOT="$GODOT_BIN"
elif command -v godot4 >/dev/null 2>&1; then
  GODOT=$(command -v godot4)
elif command -v godot >/dev/null 2>&1; then
  GODOT=$(command -v godot)
else
  echo "Godot 4 is not installed. Set GODOT_BIN=/path/to/Godot_v4.x-stable_linux.x86_64." >&2
  exit 127
fi
HEADLESS=()
USER_ARGS=()
WANTS_CAPTURE=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --headless) HEADLESS=(--headless); shift ;;
    --capture) WANTS_CAPTURE=1; USER_ARGS+=("$1"); shift; if [ "$#" -gt 0 ]; then USER_ARGS+=("$1"); shift; fi ;;
    *) USER_ARGS+=("$1"); shift ;;
  esac
done
if [ "$WANTS_CAPTURE" -eq 1 ] && [ "${#HEADLESS[@]}" -gt 0 ]; then
  echo "Capture requires a display-backed renderer; Godot's dummy --headless renderer has no readable root viewport." >&2
  echo "Use a normal display session or Xvfb/Mesa for deterministic off-screen capture." >&2
  exit 2
fi
exec "$GODOT" "${HEADLESS[@]}" --path "$ROOT/display/godot" -- "${USER_ARGS[@]}"
