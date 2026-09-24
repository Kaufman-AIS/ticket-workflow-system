#!/bin/sh
set -eu

: "${PACA_API_KEY:?PACA_API_KEY is required}"
: "${PACA_API_URL:=https://paca.kaufman-ais.com}"
: "${PUBLIC_BASE_URL:?PUBLIC_BASE_URL is required}"
: "${OWNER_TOKEN:?OWNER_TOKEN is required}"

mkdir -p "${STATE_DIR:-/data/gateway-state}"

export PACA_API_KEY PACA_API_URL
export PATH="/app/node_modules/.bin:${PATH}"

UPSTREAM_PORT="${UPSTREAM_PORT:-8770}"
GATEWAY_PORT="${GATEWAY_PORT:-8771}"

echo "[bridge] starting mcp-proxy → @paca-ai/paca-mcp (${PACA_API_URL})"
mcp-proxy \
  --port "${UPSTREAM_PORT}" \
  --server stream \
  -- \
  paca &
PROXY_PID=$!

cleanup() {
  kill "$PROXY_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait_port() {
  host="$1"
  port="$2"
  i=0
  while [ "$i" -lt 60 ]; do
    if node -e "const n=require('net');const s=n.connect(${port},'${host}',()=>{s.end();process.exit(0)});s.on('error',()=>process.exit(1))" \
      >/dev/null 2>&1; then
      return 0
    fi
    i=$((i + 1))
    sleep 0.5
  done
  return 1
}

if ! wait_port 127.0.0.1 "${UPSTREAM_PORT}"; then
  echo "[bridge] mcp-proxy did not open port ${UPSTREAM_PORT}" >&2
  exit 1
fi
echo "[bridge] mcp-proxy is up on :${UPSTREAM_PORT}"

if ! kill -0 "$PROXY_PID" 2>/dev/null; then
  echo "[bridge] mcp-proxy exited during startup" >&2
  exit 1
fi

echo "[bridge] starting OAuth gateway on :${GATEWAY_PORT} (public ${PUBLIC_BASE_URL}/mcp)"
exec node gateway.mjs
