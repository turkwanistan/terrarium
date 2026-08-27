#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

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

is_terrarium() {
  local p="$1"
  local frame
  if frame="$(curl -fsS --max-time 0.75 "http://127.0.0.1:${p}/api/frame" 2>/dev/null)"; then
    printf '%s' "$frame" | grep -q '"schema":"terrarium.frame.v1"'
  else
    return 1
  fi
}

is_occupied() {
  "$python_bin" - "$1" <<'PY'
import socket, sys
port=int(sys.argv[1])
s=socket.socket(); s.settimeout(0.35)
try:
    occupied=s.connect_ex(("127.0.0.1", port)) == 0
finally:
    s.close()
raise SystemExit(0 if occupied else 1)
PY
}

explicit_port="${TERRARIUM_PORT:-}"
if [[ -n "$explicit_port" ]]; then
  port="$explicit_port"
  if is_terrarium "$port"; then
    echo "Terrarium is already running on port ${port}; reusing the existing world process."
  elif is_occupied "$port"; then
    echo "Port ${port} is already in use by a non-Terrarium process." >&2
    echo "Identify it with:  sudo ss -ltnp 'sport = :${port}'" >&2
    echo "Or omit TERRARIUM_PORT and Terrarium will choose a free port automatically." >&2
    exit 98
  else
    port_state="free"
  fi
else
  # Prefer a stable Terrarium-specific range instead of common service ports 8080/8081.
  port=""
  for candidate in $(seq 8765 8799); do
    if is_terrarium "$candidate"; then
      port="$candidate"
      echo "Terrarium is already running on port ${candidate}; reusing the existing world process."
      break
    fi
  done
  if [[ -z "$port" ]]; then
    for candidate in $(seq 8765 8799); do
      if ! is_occupied "$candidate"; then
        port="$candidate"
        port_state="free"
        break
      fi
    done
  fi
  if [[ -z "$port" ]]; then
    echo "No free Terrarium LAN port found in 8765-8799." >&2
    echo "Set one explicitly, e.g. TERRARIUM_PORT=9000 ./scripts/run_lan.sh" >&2
    exit 98
  fi
fi

local_url="http://127.0.0.1:${port}"
lan_url="http://${ip}:${port}"

if is_terrarium "$port"; then
  echo "Local: ${local_url}/"
  if [[ -n "$ip" ]]; then
    echo "From another PC on this LAN: ${lan_url}/"
    echo "Snapshot gallery: ${lan_url}/snapshots/"
  fi
  exit 0
fi

echo "Starting Terrarium on the trusted LAN. The browser/API are read-only, but there is no authentication yet."
echo "Runtime state: ${data_dir}"
echo "Selected port: ${port}"
echo "Local: ${local_url}/"
if [[ -n "$ip" ]]; then
  echo "From another PC on this LAN: ${lan_url}/"
  echo "Snapshot gallery: ${lan_url}/snapshots/"
fi
exec "$python_bin" -m terrarium.api.server --host 0.0.0.0 --port "$port" --data-dir "$data_dir" --seed 1701 --tick-seconds 1
