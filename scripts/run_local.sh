#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v python3 >/dev/null 2>&1; then
  python_bin="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  python_bin="$(command -v python)"
else
  echo "Terrarium requires Python 3.10+ but no python3/python executable was found." >&2
  exit 127
fi

port="${TERRARIUM_PORT:-8080}"
state_root="${XDG_STATE_HOME:-$HOME/.local/state}"
data_dir="${TERRARIUM_DATA_DIR:-$state_root/terrarium/live}"
legacy_dir="$PWD/data/live"
mkdir -p "$data_dir"
"$python_bin" tools/migrate_runtime_state.py "$legacy_dir" "$data_dir" >/dev/null

"$python_bin" -m terrarium.api.server --host 127.0.0.1 --port "$port" --data-dir "$data_dir" --seed 1701 --tick-seconds 1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 30); do curl -fsS "http://127.0.0.1:${port}/api/health" >/dev/null 2>&1 && break; sleep .25; done
if command -v xdg-open >/dev/null; then xdg-open "http://127.0.0.1:${port}/" >/dev/null 2>&1 || true; elif command -v open >/dev/null; then open "http://127.0.0.1:${port}/" || true; fi
echo "Runtime state: $data_dir"
echo "Terrarium: http://127.0.0.1:${port}/"
echo "Snapshots: http://127.0.0.1:${port}/snapshots/"
wait "$pid"
