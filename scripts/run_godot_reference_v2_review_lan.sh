#!/usr/bin/env bash
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PORT=${TERRARIUM_REFERENCE_V2_REVIEW_PORT:-8878}
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/terrarium-godot-reference-v2-review"
LOG="$STATE_DIR/server.log"
PIDFILE="$STATE_DIR/server.pid"
mkdir -p "$STATE_DIR"
python_bin=$(command -v python3 || command -v python || true)
if [ -z "$python_bin" ]; then echo "Python 3 is required." >&2; exit 127; fi
PAGE="artifacts/godot-art-gate/reference-v3-review.html"
if [ ! -f "$ROOT/$PAGE" ]; then echo "Missing v2 review page." >&2; exit 2; fi
if curl -fsS --max-time 0.5 "http://127.0.0.1:${PORT}/${PAGE}" >/dev/null 2>&1; then
  ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  echo "Godot presentation candidate review is already running."
  echo "Open: http://${ip:-127.0.0.1}:${PORT}/${PAGE}"
  exit 0
fi
if [ -f "$PIDFILE" ]; then
  old_pid=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then kill "$old_pid" 2>/dev/null || true; sleep 0.2; fi
  rm -f "$PIDFILE"
fi
nohup "$python_bin" -m http.server "$PORT" --bind 0.0.0.0 --directory "$ROOT" >"$LOG" 2>&1 </dev/null &
pid=$!
echo "$pid" > "$PIDFILE"
sleep 0.4
if ! kill -0 "$pid" 2>/dev/null; then echo "Review server failed. Log: $LOG" >&2; exit 1; fi
ip=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "Godot presentation candidate review started (PID $pid)."
echo "Open from your dev PC: http://${ip:-127.0.0.1}:${PORT}/${PAGE}"
