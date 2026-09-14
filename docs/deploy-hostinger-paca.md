# Deploy Paca on Hostinger (lean)

Run Paca on the existing Hostinger VPS next to Onyx, Haystack, and Witdem. This is a **lean** deploy: Paca’s built-in AI agent is disabled; OpenAI remains in Onyx/Haystack only.

Design: [superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md](superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md)

## Prerequisites

- SSH access to the Hostinger VPS
- Docker and Docker Compose on the VPS
- Host nginx + certbot (same pattern as Onyx/Witdem)
- DNS control for `kaufman-ais.com`

## 1. DNS

Create an **A** record:

| Name | Type | Value |
| --- | --- | --- |
| `paca.kaufman-ais.com` | A | `187.124.175.57` |

Wait for propagation before requesting a certificate.

## 2. Prepare directory on VPS

```bash
mkdir -p /opt/ticket-workflow-system/paca
cd /opt/ticket-workflow-system/paca
```

Copy deploy artifacts from this repo (or clone the repo and copy `deploy/paca/*` and nginx config).

## 3. Download Paca release compose

```bash
curl -fsSL -o docker-compose.yml \
  https://github.com/Paca-AI/paca/releases/latest/download/docker-compose.yml
```

Download any gateway assets bundled with the release (Caddyfile, nginx config, etc.) if required by the release notes.

If the gateway service in `docker-compose.yml` is not named `caddy`, update `docker-compose.override.yml` accordingly — see [deploy/paca/README.md](../deploy/paca/README.md).

## 4. Configure environment

```bash
cp .env.example .env
# Generate secrets: openssl rand -hex 32
```

Fill all empty values in `.env`:

- `JWT_SECRET`, `POSTGRES_PASSWORD`, `INTERNAL_API_KEY`, `ENCRYPTION_KEY` — use `openssl rand -hex 32`
- `ADMIN_PASSWORD` — strong password for the Paca admin user
- `AGENT_API_KEY` — optional for lean deploy (built-in agent is off); can leave empty or set for future use
- `PUBLIC_URL` — keep `https://paca.kaufman-ais.com`

Never commit `.env` to git.

## 5. Start Paca (no built-in AI agent)

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml --env-file .env up -d --scale ai-agent=0
```

Verify containers are healthy:

```bash
docker compose ps
curl -fsS http://127.0.0.1:8090/ | head -c 500
```

## 6. Install nginx site and TLS

Copy the nginx site config:

```bash
sudo cp deploy/nginx/paca.kaufman-ais.com.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/paca.kaufman-ais.com.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Obtain certificate:

```bash
sudo certbot --nginx -d paca.kaufman-ais.com
```

Reload nginx after certbot if needed.

## 7. Verify public URL

```bash
curl -fsS https://paca.kaufman-ais.com/
```

Expect HTTP **200** or **302** with HTML (login or app shell). A redirect to HTTPS is fine.

Optional: run `scripts/smoke_paca_health.sh` after Task 3 is merged.

## 8. Create API key

1. Open `https://paca.kaufman-ais.com/` in a browser.
2. Log in with the admin credentials from `.env`.
3. Go to **Settings → API Keys** and create a key.
4. Store the key in client environments only (Haystack, Onyx MCP, Cursor local) — never in this repo.

## Lean deploy notes

- **`ai-agent` is scaled to zero** — no Goose sandboxes or Paca-native LLM on this VPS.
- **OpenAI** is used only through existing Onyx/Haystack agents, not Paca’s LLM settings.
- Clients integrate via `@paca-ai/paca-mcp` and the Paca REST API.
- Paca still runs Postgres, Valkey, and MinIO; confirm VPS memory/disk headroom before go-live.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `502` from nginx | `docker compose ps`; is anything listening on `127.0.0.1:8090`? |
| Wrong gateway service | Rename service in `docker-compose.override.yml` to match release compose |
| Certbot fails | DNS A record points to `187.124.175.57`; port 80 reachable |
| Auth errors from MCP | API key created in UI; `PUBLIC_URL` matches browser URL |
