#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
port="${TERRARIUM_PORT:-8080}"
ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo "Starting Terrarium on the trusted LAN. The browser/API are read-only, but there is no authentication yet."
echo "Local: http://127.0.0.1:${port}/"
if [[ -n "${ip}" ]]; then
  echo "From another PC on this LAN: http://${ip}:${port}/"
  echo "Snapshot gallery: http://${ip}:${port}/snapshots/"
fi
exec python -m terrarium.api.server --host 0.0.0.0 --port "${port}" --data-dir data/live --seed 1701 --tick-seconds 1
