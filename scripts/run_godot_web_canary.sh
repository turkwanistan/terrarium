#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
WEB_ROOT="$ROOT/display/web/godot"
PORT="${TERRARIUM_GODOT_WEB_PORT:-8766}"

python_bin="$(command -v python3 || command -v python || true)"
if [[ -z "$python_bin" ]]; then
  echo "Terrarium Godot web gateway requires Python 3.10+." >&2
  exit 127
fi
if ! command -v openssl >/dev/null 2>&1; then
  echo "Terrarium Godot web gateway requires openssl for its local HTTPS certificate." >&2
  exit 127
fi
if [[ ! -f "$WEB_ROOT/index.html" ]]; then
  echo "Godot web build is not present in this checkout: $WEB_ROOT/index.html" >&2
  echo "Push the web-cutover source commit and let the repository's Godot Web build workflow produce it, then pull the generated build." >&2
  exit 66
fi

if ! "$python_bin" - "$PORT" <<'PY'
import socket
import sys
port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
except OSError as exc:
    print(f"Terrarium Godot web presentation port {port} is already in use: {exc}", file=sys.stderr)
    raise SystemExit(1)
finally:
    sock.close()
PY
then
  echo "Choose another port with TERRARIUM_GODOT_WEB_PORT=<port>, or stop the stale presentation gateway." >&2
  exit 98
fi

is_frame_endpoint() {
  "$python_bin" - "$1" <<'PY'
import sys
from urllib.request import urlopen
base=sys.argv[1].rstrip('/')
try:
    with urlopen(base + '/api/frame', timeout=0.75) as r:
        raw=r.read()
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if r.status == 200 and b'"schema":"terrarium.frame.v1"' in raw else 1)
PY
}

api_url="${TERRARIUM_API_URL:-}"
if [[ -n "$api_url" ]]; then
  api_url="${api_url%/}"
  if ! is_frame_endpoint "$api_url"; then
    echo "TERRARIUM_API_URL does not expose a readable terrarium.frame.v1 endpoint: $api_url" >&2
    exit 69
  fi
else
  for candidate_port in $(seq 8765 8799) 8080; do
    candidate="http://127.0.0.1:${candidate_port}"
    if is_frame_endpoint "$candidate"; then
      api_url="$candidate"
      break
    fi
  done
  if [[ -z "$api_url" ]]; then
    echo "No running canonical Terrarium /api/frame endpoint found." >&2
    echo "Start/reuse the living world separately with ./scripts/run_lan.sh." >&2
    exit 69
  fi
fi

ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
if [[ -z "$ip" ]]; then
  ip="127.0.0.1"
fi
hostname_short="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo terrarium)"
state_home="${XDG_STATE_HOME:-$HOME/.local/state}"
tls_dir="$state_home/terrarium/godot-web/tls"
cert="$tls_dir/terrarium-local.crt"
key="$tls_dir/terrarium-local.key"
config="$tls_dir/openssl.cnf"
mkdir -p "$tls_dir"
chmod 700 "$tls_dir"

if [[ ! -s "$cert" || ! -s "$key" ]]; then
  cat >"$config" <<EOF
[req]
distinguished_name=dn
x509_extensions=v3_req
prompt=no

[dn]
CN=Terrarium Local

[v3_req]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
IP.1=$ip
DNS.1=terrarium.local
DNS.2=$hostname_short
EOF
  openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 825 \
    -keyout "$key" -out "$cert" -config "$config" >/dev/null 2>&1
  chmod 600 "$key"
  chmod 644 "$cert"
fi

url="https://${ip}:${PORT}/"
canvas_url="${api_url/127.0.0.1/$ip}/"

echo "Terrarium Godot web canary"
echo "Canonical API (read-only upstream): $api_url"
echo "Godot browser presentation: $url"
echo "Canvas rollback: $canvas_url"
echo ""
echo "The local certificate is intentionally self-signed for canary UAT."
echo "Your browser may require a one-time Advanced/Proceed confirmation."

exec "$python_bin" "$ROOT/tools/godot_web_gateway.py" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --upstream "$api_url" \
  --web-root "$WEB_ROOT" \
  --cert "$cert" \
  --key "$key"
