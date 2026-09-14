# Cursor MCP via SSH tunnel (no public DNS yet)

Until `paca.kaufman-ais.com` has a public A record and TLS, use an SSH tunnel
from your laptop to the Hostinger gateway bind.

## Tunnel

```bash
ssh -N -L 18090:127.0.0.1:8090 deploy@187.124.175.57
```

Leave that terminal open. Paca is then reachable at `http://127.0.0.1:18090`.

## Cursor MCP config

Copy [`config/cursor-mcp.example.json`](../config/cursor-mcp.example.json) and set:

```json
{
  "mcpServers": {
    "paca": {
      "command": "npx",
      "args": ["-y", "@paca-ai/paca-mcp"],
      "env": {
        "PACA_API_KEY": "paca_…",
        "PACA_API_URL": "http://127.0.0.1:18090"
      }
    }
  }
}
```

Create the API key in Paca (Settings → API Keys) after logging in through the
tunnel in a browser: open `http://127.0.0.1:18090/` (admin password is in
`/opt/ticket-workflow-system/paca/.env` on the VPS — do not commit it).

## Smoke prompts

- List projects
- Create a task titled `cursor-tunnel-smoke`
- Create a document with a short markdown body

## API smoke without MCP

```bash
export PACA_API_URL=http://127.0.0.1:18090
export PACA_API_KEY=paca_…
export PACA_PROJECT_ID=<project-uuid>
python scripts/smoke_paca_api.py
```

When public DNS + certbot succeed, switch `PACA_API_URL` to
`https://paca.kaufman-ais.com` and drop the tunnel.
