# ChatGPT-facing OAuth gateway + Streamable HTTP bridge for @paca-ai/paca-mcp
FROM node:22-bookworm-slim

WORKDIR /app

# Minimal tools for health waits
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

COPY package.json ./
RUN npm install --omit=dev

COPY gateway.mjs entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENV GATEWAY_HOST=0.0.0.0 \
    GATEWAY_PORT=8771 \
    UPSTREAM_HOST=127.0.0.1 \
    UPSTREAM_PORT=8770 \
    UPSTREAM_PATH=/mcp \
    MCP_PATH=/mcp \
    SCOPE=mcp \
    RESOURCE_NAME=Paca \
    STATE_DIR=/data/gateway-state \
    PACA_API_URL=https://paca.kaufman-ais.com

VOLUME ["/data"]
EXPOSE 8771

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${GATEWAY_PORT}/healthz" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
