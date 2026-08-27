#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m terrarium.api.server --host 127.0.0.1 --port 8080 --data-dir data/live --seed 1701 --tick-seconds 1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 30); do curl -fsS http://127.0.0.1:8080/api/health >/dev/null 2>&1 && break; sleep .25; done
if command -v xdg-open >/dev/null; then xdg-open http://127.0.0.1:8080/ >/dev/null 2>&1 || true; elif command -v open >/dev/null; then open http://127.0.0.1:8080/ || true; fi
echo "Terrarium: http://127.0.0.1:8080/"
echo "Snapshots: http://127.0.0.1:8080/snapshots/"
wait "$pid"
