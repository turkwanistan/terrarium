#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

port="${TERRARIUM_PORT:-8080}"
ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
python_bin="$(command -v python3 || command -v python || true)"
if [[ -z "$python_bin" ]]; then
  echo "Terrarium requires Python 3.10+; neither python3 nor python was found." >&2
  exit 127
fi

state_home="${XDG_STATE_HOME:-$HOME/.local/state}"
data_dir="${TERRARIUM_DATA_DIR:-$state_home/terrarium/live}"
legacy_root="$(pwd)/data/live"

if [[ ! -f "$data_dir/terrarium.sqlite3" && -f "$legacy_root/terrarium.sqlite3" ]]; then
  echo "Migrating existing Terrarium state to user-owned runtime storage..."
  "$python_bin" tools/migrate_runtime_state.py "$legacy_root" "$data_dir"
fi
mkdir -p "$data_dir"

local_url="http://127.0.0.1:${port}"
lan_url="http://${ip}:${port}"

# A running Terrarium is a valid singleton: don't try to start a second world.
if frame="$(curl -fsS --max-time 1 "$local_url/api/frame" 2>/dev/null)"; then
  if printf '%s' "$frame" | grep -q '"schema":"terrarium.frame.v1"'; then
    echo "Terrarium is already running on port ${port}; reusing the existing world process."
    echo "Local: ${local_url}/"
    if [[ -n "$ip" ]]; then
      echo "From another PC on this LAN: ${lan_url}/"
      echo "Snapshot gallery: ${lan_url}/snapshots/"
    fi
    exit 0
  fi
fi

# If anything else owns the port, fail before opening SQLite or starting the world.
if "$python_bin" - "$port" <<'PY'
import socket, sys
port=int(sys.argv[1])
s=socket.socket(); s.settimeout(0.5)
try:
    occupied=s.connect_ex(("127.0.0.1", port)) == 0
finally:
    s.close()
raise SystemExit(0 if occupied else 1)
PY
then
  echo "Port ${port} is already in use by a non-Terrarium process." >&2
  echo "Identify it with:  sudo ss -ltnp 'sport = :${port}'" >&2
  echo "Or start Terrarium on another port, e.g.: TERRARIUM_PORT=8081 ./scripts/run_lan.sh" >&2
  exit 98
fi

echo "Starting Terrarium on the trusted LAN. The browser/API are read-only, but there is no authentication yet."
echo "Runtime state: ${data_dir}"
echo "Local: ${local_url}/"
if [[ -n "$ip" ]]; then
  echo "From another PC on this LAN: ${lan_url}/"
  echo "Snapshot gallery: ${lan_url}/snapshots/"
fi
exec "$python_bin" -m terrarium.api.server --host 0.0.0.0 --port "$port" --data-dir "$data_dir" --seed 1701 --tick-seconds 1
