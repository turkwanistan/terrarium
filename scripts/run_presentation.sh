#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mode="godot"

usage() {
  cat <<'EOF'
Usage: ./scripts/run_presentation.sh [--godot|--canvas]

Normal presentation: Godot (read-only canonical /api/frame consumer).
Rollback/fallback:    Canvas browser renderer against the same canonical world.

The canonical world/API must already be running. This script never starts,
steps, migrates, resets, or stops the living world.

Set TERRARIUM_API_URL=http://host:port to select a specific canonical API.
EOF
}

case "${1:-}" in
  ""|--godot)
    mode="godot"
    ;;
  --canvas)
    mode="canvas"
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 64
    ;;
esac
if [[ $# -gt 1 ]]; then
  usage >&2
  exit 64
fi

# The normal presentation delegates to the already-validated read-only Godot
# launcher. Keeping world lifecycle outside this selector ensures a renderer
# failure cannot stop, reset, migrate, or recreate Moss's world.
if [[ "$mode" == "godot" ]]; then
  echo "Terrarium presentation: Godot (normal)"
  echo "Canvas rollback: ./scripts/run_presentation.sh --canvas"
  exec "$ROOT/scripts/run_godot_live_candidate.sh"
fi

is_frame_endpoint() {
  local base="$1"
  curl -fsS --max-time 0.75 "$base/api/frame" 2>/dev/null \
    | grep -q '"schema":"terrarium.frame.v1"'
}

api_url="${TERRARIUM_API_URL:-}"
if [[ -n "$api_url" ]]; then
  api_url="${api_url%/}"
  if ! is_frame_endpoint "$api_url"; then
    echo "TERRARIUM_API_URL does not expose a readable terrarium.frame.v1 endpoint: $api_url" >&2
    exit 69
  fi
else
  for port in $(seq 8765 8799) 8080; do
    candidate="http://127.0.0.1:${port}"
    if is_frame_endpoint "$candidate"; then
      api_url="$candidate"
      break
    fi
  done
  if [[ -z "$api_url" ]]; then
    echo "No running canonical Terrarium /api/frame endpoint found." >&2
    echo "Start/reuse the world separately with ./scripts/run_lan.sh or set TERRARIUM_API_URL." >&2
    exit 69
  fi
fi

canvas_url="$api_url/"
echo "Terrarium presentation: Canvas fallback"
echo "Canonical API (read-only): $api_url"
echo "Canvas: $canvas_url"

# Useful on a headless world host: resolve/print the rollback URL without
# pretending the host itself is a presentation machine.
if [[ "${TERRARIUM_CANVAS_PRINT_ONLY:-0}" == "1" ]]; then
  exit 0
fi

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$canvas_url" >/dev/null 2>&1 || {
    echo "Could not open a browser automatically; open: $canvas_url" >&2
    exit 70
  }
elif command -v open >/dev/null 2>&1; then
  open "$canvas_url" || {
    echo "Could not open a browser automatically; open: $canvas_url" >&2
    exit 70
  }
else
  echo "No desktop URL opener found; open this URL in a browser: $canvas_url"
fi
