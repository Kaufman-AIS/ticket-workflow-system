# Cursor MCP — Paca

Connect Cursor to the lean Paca instance at `https://paca.kaufman-ais.com` via the official [`@paca-ai/paca-mcp`](https://www.npmjs.com/package/@paca-ai/paca-mcp) server.

Design context: [superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md](superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md)

## Prerequisites

- Node.js 18+ (for `npx`)
- A Paca **API key** with access to at least one project (create in Paca admin → Settings → API keys)
- Paca deployed and reachable (see [deploy-hostinger-paca.md](deploy-hostinger-paca.md))

## Configure Cursor

1. Open **Cursor Settings → MCP** (or edit your MCP config file directly).
2. Merge the example server block from [`config/cursor-mcp.example.json`](../config/cursor-mcp.example.json):

```json
{
  "mcpServers": {
    "paca": {
      "command": "npx",
      "args": ["-y", "@paca-ai/paca-mcp"],
      "env": {
        "PACA_API_KEY": "REPLACE_ME",
        "PACA_API_URL": "https://paca.kaufman-ais.com"
      }
    }
  }
}
```

3. Replace `REPLACE_ME` with your real API key. **Never commit the key** — keep it in Cursor local settings or a secrets manager.
4. Save and restart Cursor (or reload MCP servers from the MCP panel).
5. Confirm the **paca** server shows as connected in the MCP tools list.

### Environment variables

| Variable | Value |
| --- | --- |
| `PACA_API_URL` | `https://paca.kaufman-ais.com` |
| `PACA_API_KEY` | Your Paca API key (Bearer token) |

## Smoke prompts (Agent chat)

Run these in **Cursor Agent** after MCP is connected. Each prompt should invoke Paca MCP tools (not REST directly).

1. **List projects**

   > List my Paca projects.

   Expect: a list of project names/IDs from the connected Paca instance.

2. **Create task**

   > In Paca, create a task titled `cursor-smoke` with description `Cursor MCP smoke test`.

   Expect: confirmation with a new task ID; task visible in the Paca web UI under the target project.

3. **Create document**

   > In Paca, create a document titled `cursor-smoke-doc` with this markdown body:
   >
   > ```markdown
   > # Cursor smoke
   >
   > Created via Cursor MCP.
   > ```

   Expect: confirmation with a new document ID; document visible in Paca.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| MCP server fails to start | `npx -y @paca-ai/paca-mcp` runs locally; Node 18+ installed |
| 401 / auth errors | API key valid; `PACA_API_URL` matches live instance |
| Tools missing | Reload MCP; confirm `paca` server is enabled |
| Wrong project | Specify project name/ID in the prompt, or create a default project in Paca admin first |

## Related checks

- HTTPS / login page: `./scripts/smoke_paca_health.sh https://paca.kaufman-ais.com`
- REST API (CI/VPS, no MCP): `scripts/smoke_paca_api.py` with `PACA_API_URL`, `PACA_API_KEY`, `PACA_PROJECT_ID`
