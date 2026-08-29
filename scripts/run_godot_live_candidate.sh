#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PROJECT="$ROOT/display/godot_reference_v2"

# This launcher is deliberately presentation-only. It never starts/steps/migrates
# the canonical world and never regenerates production art at runtime.
if [[ ! -f "$PROJECT/project.godot" || ! -f "$PROJECT/art/hero_manifest.json" ]]; then
  echo "Godot presentation candidate is not generated/validated in this checkout." >&2
  exit 66
fi

GODOT_BIN="${GODOT_BIN:-}"
if [[ -z "$GODOT_BIN" ]]; then
  if command -v godot4 >/dev/null 2>&1; then
    GODOT_BIN="$(command -v godot4)"
  elif command -v godot >/dev/null 2>&1; then
    GODOT_BIN="$(command -v godot)"
  else
    echo "Godot 4 not found. Set GODOT_BIN=/path/to/godot." >&2
    exit 127
  fi
fi

# Do not accidentally recreate the Lab llvmpipe incident on a headless host.
# Native validation in mcp-lab uses the bounded GODOT_NATIVE_VALIDATION.md path.
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" && "${TERRARIUM_GODOT_HEADLESS_OK:-0}" != "1" ]]; then
  echo "Refusing unbounded Godot live launch without DISPLAY/WAYLAND_DISPLAY." >&2
  echo "For intentional headless testing use the bounded Lab validation procedure; override only with TERRARIUM_GODOT_HEADLESS_OK=1." >&2
  exit 78
fi
if command -v glxinfo >/dev/null 2>&1 && glxinfo -B 2>/dev/null | grep -qi 'llvmpipe'; then
  if [[ "${TERRARIUM_GODOT_SOFTWARE_RENDER_OK:-0}" != "1" ]]; then
    echo "Refusing live Godot launch on Mesa llvmpipe software rendering." >&2
    echo "Set TERRARIUM_GODOT_SOFTWARE_RENDER_OK=1 only for an intentional bounded test." >&2
    exit 78
  fi
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

echo "Terrarium Godot live candidate"
echo "Canonical API (read-only): $api_url"
echo "Canvas remains available as the current fallback; this command performs no cutover."
exec "$GODOT_BIN" --path "$PROJECT" -- --live --api-url "$api_url"
