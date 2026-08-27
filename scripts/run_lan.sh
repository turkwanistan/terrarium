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
ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
state_root="${XDG_STATE_HOME:-$HOME/.local/state}"
data_dir="${TERRARIUM_DATA_DIR:-$state_root/terrarium/live}"
legacy_dir="$PWD/data/live"

mkdir -p "$data_dir"
"$python_bin" tools/migrate_runtime_state.py "$legacy_dir" "$data_dir" >/dev/null

echo "Starting Terrarium on the trusted LAN. The browser/API are read-only, but there is no authentication yet."
echo "Runtime state: $data_dir"
echo "Local: http://127.0.0.1:${port}/"
if [[ -n "${ip}" ]]; then
  echo "From another PC on this LAN: http://${ip}:${port}/"
  echo "Snapshot gallery: http://${ip}:${port}/snapshots/"
fi
exec "$python_bin" -m terrarium.api.server --host 0.0.0.0 --port "$port" --data-dir "$data_dir" --seed 1701 --tick-seconds 1
