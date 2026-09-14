# Paca deploy (lean)

Lean Paca on the Hostinger VPS: official release compose, **no built-in AI agent** (`ai-agent` scaled to zero). OpenAI stays in Onyx/Haystack; clients connect via MCP and the Paca API.

Full checklist: [docs/deploy-hostinger-paca.md](../../docs/deploy-hostinger-paca.md).

## Files in this directory

| File | Purpose |
| --- | --- |
| `.env.example` | Required env vars — copy to `.env` on the VPS and fill secrets |
| `docker-compose.override.yml` | Bind gateway to `127.0.0.1:8090`, disable `ai-agent` |

## Fetch official release assets

On the VPS (see deploy guide for path):

```bash
curl -fsSL -o docker-compose.yml \
  https://github.com/Paca-AI/paca/releases/latest/download/docker-compose.yml
```

Download any bundled gateway config from the same release (e.g. `Caddyfile` or nginx snippets) if the release notes require it.

## Service name adjustments

The override assumes the release compose exposes HTTP on port 80 via a service named **`caddy`**. Releases may use **`nginx`** or **`web`** instead.

1. Open the downloaded `docker-compose.yml` and find the service that publishes `:80`.
2. If it is not `caddy`, rename the key under `services:` in `docker-compose.override.yml` to match (keep the same `ports` mapping).
3. Confirm the `ai-agent` service name matches; adjust the override or use `--scale ai-agent=0` on the CLI if the release uses a different name.

## Start stack

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml --env-file .env up -d --scale ai-agent=0
```

Host nginx terminates TLS and proxies to `127.0.0.1:8090` — see `deploy/nginx/paca.kaufman-ais.com.conf`.
