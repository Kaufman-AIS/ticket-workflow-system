# Paca deploy (lean)

Lean Paca on the Hostinger VPS: official release compose, **no built-in AI agent** (`agent-runner` scaled to zero). OpenAI stays in Onyx/Haystack; clients connect via MCP and the Paca API.

Full checklist: [docs/deploy-hostinger-paca.md](../../docs/deploy-hostinger-paca.md).

## Files in this directory

| File | Purpose |
| --- | --- |
| `.env.example` | Required env vars — copy to `.env` on the VPS and fill secrets |
| `docker-compose.override.yml` | Bind `gateway` to `127.0.0.1:8090` (use `--scale agent-runner=0`) |

## Fetch official release assets

On the VPS (see deploy guide for path):

```bash
curl -fsSL -o docker-compose.yml \
  https://github.com/Paca-AI/paca/releases/latest/download/docker-compose.yml
```

Download any bundled gateway config from the same release (e.g. `Caddyfile` or nginx snippets) if the release notes require it.

## Service name adjustments

Release **v0.16+** uses service **`gateway`** (Caddy image) and optional **`agent-runner`**. Older docs mentioning `caddy` / `ai-agent` as compose service names are obsolete.

## Start stack

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml --env-file .env up -d --scale agent-runner=0
```

Host nginx terminates TLS and proxies to `127.0.0.1:8090` — see `deploy/nginx/paca.kaufman-ais.com.conf`.
