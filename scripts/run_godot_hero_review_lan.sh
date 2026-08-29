#!/usr/bin/env bash
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# Keep this outside Terrarium's canonical auto-selection range (8765-8799).
PORT=${TERRARIUM_HERO_REVIEW_PORT:-8877}
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/terrarium-godot-hero-review"
LOG="$STATE_DIR/server.log"
PIDFILE="$STATE_DIR/server.pid"
mkdir -p "$STATE_DIR"
python_bin=$(command -v python3 || command -v python || true)
if [ -z "$python_bin" ]; then echo "Python 3 is required." >&2; exit 127; fi
if [ ! -f "$ROOT/artifacts/godot-art-gate/review.html" ]; then echo "Missing hero review page." >&2; exit 2; fi
if curl -fsS --max-time 0.5 "http://127.0.0.1:${PORT}/artifacts/godot-art-gate/review.html" >/dev/null 2>&1; then
  ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  echo "Terrarium hero review is already running."
  echo "Open: http://${ip:-127.0.0.1}:${PORT}/artifacts/godot-art-gate/review.html"
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
if ! kill -0 "$pid" 2>/dev/null; then echo "Review server failed to start. Log: $LOG" >&2; tail -n 20 "$LOG" >&2 2>/dev/null || true; rm -f "$PIDFILE"; exit 1; fi
ip=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "Terrarium hero review started in the background (PID $pid)."
echo "Open from your dev PC: http://${ip:-127.0.0.1}:${PORT}/artifacts/godot-art-gate/review.html"
echo "Log: $LOG"
