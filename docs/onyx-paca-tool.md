# Onyx — Paca tool wiring (v1)

How to give Onyx agents access to Paca tasks and documents on the lean Hostinger deploy.

Design context: [superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md](superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md)

## v1 approach: OpenAPI tool → Paca REST

Onyx custom tools are defined via **OpenAPI** specs. For v1, wire tools that call the same REST endpoints used by [`integrations/paca_client`](../integrations/paca_client/client.py) — not a separate MCP bridge unless Onyx MCP support is enabled on your deployment.

| Concern | v1 choice |
| --- | --- |
| Transport | HTTPS + Bearer `PACA_API_KEY` |
| Base URL | `https://paca.kaufman-ais.com` (or internal `http://127.0.0.1:8090` from VPS) |
| MCP | Optional later; Cursor/Haystack use MCP or REST as documented elsewhere |

### Endpoints mirrored by `PacaClient`

| Operation | Method | Path | Body / params |
| --- | --- | --- | --- |
| Create task | `POST` | `/api/v1/tasks` | `project_id`, `title`, optional `description` |
| Update task | `PATCH` | `/api/v1/tasks/{task_id}` | fields to patch |
| List tasks | `GET` | `/api/v1/tasks` | `project_id` query param |
| Create document | `POST` | `/api/v1/documents` | `project_id`, `title`, `content` (markdown) |
| Update document | `PATCH` | `/api/v1/documents/{document_id}` | `title`, `content` |

Confirm paths against live OpenAPI on the Paca instance before go-live (Task 7). If paths differ, update `PacaClient` and this doc together.

## Registering tools in Onyx

1. In Onyx admin, open **Tools** (or **Custom Tools** / OpenAPI tool configuration — exact label depends on Onyx version).
2. Add an OpenAPI tool with:
   - **Server URL**: `https://paca.kaufman-ais.com` (external) or an internal helper URL on the VPS (see below).
   - **Authentication**: Bearer token header; value from env `PACA_API_KEY` (store in Onyx secrets / VPS env, never in git).
3. Expose at minimum these operations for intake/smoke parity:
   - `create_task`
   - `create_document`
   - `list_tasks` (optional for board views)
4. Attach the tool to the persona(s) that run document intake or board-member workflows.

### Internal helper URL (Task 10)

When Onyx wiring lands on the VPS, a tiny **FastAPI sidecar** (or existing Haystack service) can expose a narrow OpenAPI surface that wraps `PacaClient` and hides project scoping:

- Env on VPS: `PACA_API_URL`, `PACA_API_KEY`, `PACA_PROJECT_ID`
- Onyx OpenAPI tool points at `http://127.0.0.1:<port>/...` on localhost only
- Sidecar validates caller (e.g. internal API key) before forwarding to Paca

Until that sidecar exists, point Onyx OpenAPI directly at Paca’s public API with a scoped API key.

## MCP alternative (optional)

If your Onyx build supports **MCP tool servers**, you can run the same config as Cursor:

```json
{
  "command": "npx",
  "args": ["-y", "@paca-ai/paca-mcp"],
  "env": {
    "PACA_API_KEY": "<from secrets>",
    "PACA_API_URL": "https://paca.kaufman-ais.com"
  }
}
```

Prefer OpenAPI + `PacaClient` paths for v1 unless MCP is already operational on the VPS — fewer moving parts and identical behaviour to Haystack REST usage.

## Smoke (Onyx chat)

After tools are registered:

> Create a Paca task titled `onyx-smoke` with description `Onyx tool smoke test`.

> Create a Paca document titled `onyx-smoke-doc` with markdown `# Onyx smoke`.

Verify in the Paca web UI and in Witdem run evidence if the turn is proxied.

## Board-member helpers (Task 10)

Task 10 adds `integrations/paca_client/board.py` (`claim_task`, `set_status`, `add_comment`) and extends this doc with OpenAPI snippets for those three tools once live API paths are confirmed.

## Secrets

| Secret | Where |
| --- | --- |
| `PACA_API_KEY` | Onyx tool auth, VPS env, GitHub Actions secret — **never commit** |
| `PACA_PROJECT_ID` | VPS env for scoped create operations |
| `PACA_API_URL` | `https://paca.kaufman-ais.com` |

## Related

- Cursor MCP setup: [cursor-mcp.md](cursor-mcp.md)
- REST smoke script: `scripts/smoke_paca_api.py`
- Deploy: [deploy-hostinger-paca.md](deploy-hostinger-paca.md)
