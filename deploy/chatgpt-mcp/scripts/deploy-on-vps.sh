#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/patch-paca-caddy.py /opt/ticket-workflow-system/paca/caddy/Caddyfile

docker rm -f paca-chatgpt-mcp 2>/dev/null || true

set -a
# shellcheck disable=SC1091
. ./.env
set +a

docker run -d --name paca-chatgpt-mcp --restart unless-stopped \
  --network paca_default \
  --memory 512m \
  -v /opt/ticket-workflow-system/chatgpt-mcp:/app \
  -v paca-chatgpt-mcp-node_modules:/app/node_modules \
  -v paca-chatgpt-mcp-state:/data \
  -e PUBLIC_BASE_URL \
  -e PACA_API_URL \
  -e PACA_API_KEY \
  -e OWNER_TOKEN \
  -e CHATGPT_ACTION_TOKEN \
  -e RESOURCE_NAME="${RESOURCE_NAME:-Paca}" \
  -e GATEWAY_HOST=0.0.0.0 \
  -e GATEWAY_PORT=8771 \
  -e UPSTREAM_HOST=127.0.0.1 \
  -e UPSTREAM_PORT=8770 \
  -e UPSTREAM_PATH=/mcp \
  -e MCP_PATH=/mcp \
  -e SCOPE=mcp \
  -e STATE_DIR=/data/gateway-state \
  -e TRUST_PROXY=loopback \
  -e ALLOWED_REDIRECT_HOSTS=chatgpt.com,localhost,127.0.0.1 \
  -w /app \
  --entrypoint ./entrypoint.sh \
  node:22-bookworm-slim

sleep 12
docker logs --tail 40 paca-chatgpt-mcp
docker exec paca-gateway-1 caddy reload --config /etc/caddy/Caddyfile
sleep 2
docker exec paca-gateway-1 wget -qO- http://paca-chatgpt-mcp:8771/healthz
echo
curl -fsS https://paca.kaufman-ais.com/healthz-mcp
echo
curl -sS -o /dev/null -w "mcp:%{http_code}\n" https://paca.kaufman-ais.com/mcp
curl -fsS https://paca.kaufman-ais.com/.well-known/oauth-authorization-server | head -c 280
echo
