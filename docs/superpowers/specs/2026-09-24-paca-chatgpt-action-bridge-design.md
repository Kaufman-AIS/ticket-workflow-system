# Paca ChatGPT Action Bridge

Date: 2026-09-24  
Status: Approved design — implementation pending

## Goal

Make all Paca capabilities usable from a Custom GPT on iOS through GPT Actions, following the working `execution-memory` pattern. The GPT imports a public OpenAPI document and calls one authenticated JSON-RPC endpoint. Paca credentials remain on the Hostinger VPS.

## Architecture

```text
Custom GPT / iOS
  -- Bearer action token --> https://paca.kaufman-ais.com/chatgpt/rpc
                              |-- validates action token
                              |-- dispatches allowed Paca methods
                              `-- X-API-Key --> Paca REST API
```

Public, secret-free assets:

- `GET /chatgpt/openapi.yaml` — OpenAPI schema for GPT Actions
- `GET /chatgpt/README.md` — setup instructions
- `GET /chatgpt/health` — unauthenticated liveness check

Protected asset:

- `POST /chatgpt/rpc` — JSON-RPC 2.0 action endpoint with Bearer authentication

## Capability scope

The bridge exposes the full Paca MCP capability set through explicit JSON-RPC methods: projects, tasks, statuses, types, sprints, views and positions, documents, comments and activities, members and roles, attachments, custom fields, automations, task links, and plugin-provided operations where supported by the installed Paca client.

Read, create, update, and delete methods are available. The GPT instructions must require confirmation before destructive operations, but the server must also reject unknown methods and malformed parameters.

## Security

- `PACA_API_KEY` is read only from the VPS environment and is never returned to ChatGPT.
- `CHATGPT_ACTION_TOKEN` is a separate high-entropy secret used only by the GPT Action.
- The action token is compared in constant time and never logged.
- OpenAPI and README routes contain no secrets.
- Errors returned to the GPT contain safe summaries, not upstream credentials or stack traces.
- The bridge does not expose arbitrary Paca URLs or arbitrary HTTP methods.

## Error handling

- Missing/invalid Bearer token: HTTP 401.
- Invalid JSON-RPC body or unknown method: JSON-RPC error response.
- Paca API failure: JSON-RPC error with HTTP 200, preserving the upstream status in structured data without leaking secrets.
- Health reports bridge and Paca reachability without returning data.

## Verification

- Unit tests cover authentication, method dispatch, OpenAPI serving, malformed requests, and upstream error translation.
- Live checks verify the OpenAPI document, unauthenticated health, 401 protection, authorized project/task read, and one safe write/read-back path.

## Non-goals

- Adding MCP support to the Custom GPT builder.
- Putting the Paca API key into the GPT configuration.
- Deleting or repairing existing Paca board data as part of this integration.
