# Paca on Hostinger + MCP workflows (design)

Date: 2026-09-14  
Repo: [Kaufman-AIS/ticket-workflow-system](https://github.com/Kaufman-AIS/ticket-workflow-system)  
Status: Approved — implementation plan at `docs/superpowers/plans/2026-09-14-paca-hostinger-mcp.md`

## Goal

Run **Paca** on the existing Hostinger VPS next to **Onyx**, **Haystack**, and **Witdem**. Connect existing OpenAI-backed agents to Paca via MCP so they can manage tickets and write documents. Witdem remains the observability layer for production runs.

Success looks like: humans and agents share the same Paca board; intake and other Haystack workflows create/update tasks and docs; Cursor and Onyx can use the same MCP surface; Witdem shows traces and outcomes including Paca tool steps.

## Non-goals (initial delivery)

- Paca’s built-in AI agent / Goose sandboxes (scale to zero).
- Configuring OpenAI API keys inside Paca’s own LLM settings.
- Replacing Onyx chat or Witdem with Paca-native features.
- Merging this work into `kaufman-ais-com` or rewriting Document Intake from scratch.

## Decisions (locked)

| Topic | Decision |
| --- | --- |
| Scope target | Full picture: board + agents + Witdem (phased delivery) |
| Agent runtime | Existing stack: Onyx → Haystack / OpenAI (not Paca built-in agents) |
| Deploy | Same Hostinger VPS; Haystack + Witdem + Onyx already there; add Paca |
| OpenAI | Only through existing Onyx/Haystack agents (not Paca LLM config) |
| Integration approach | Lean Paca + official `@paca-ai/paca-mcp` |
| MCP clients | **Haystack** (workflows), **Cursor** (dev/ops), **Onyx** (end-user chat) — all in design |
| Functional outcomes | Intake → Paca tasks; agents as board members; MCP read/write including **docs** |
| Spec / code home | This repo (`ticket-workflow-system`), public under Kaufman-AIS |

## Architecture

```text
                    ┌──────────────┐
  User ───────────►│ Onyx (+proxy) │──────┐
                    └──────────────┘      │
                                          ▼
  Cursor ──MCP──┐                   ┌──────────┐     OpenAI
                ├──────────────────►│ Paca API │◄── (not used here)
  Haystack ─MCP─┘                   │ Web/DB/… │
       │                            └──────────┘
       │ workflows                         ▲
       ▼                                   │
  OpenAI LLM                        MCP tools:
       │                            tasks, docs, status,
       ▼                            comments, members
  Witdem ◄── traces + outcomes (Haystack / Onyx runs; MCP spans when instrumented)
```

**Hostinger VPS (existing):** Onyx (`onyx.kaufman-ais.com`), Witdem (`demo.witdem.com`), Haystack intake / related compose.  
**New:** Paca stack (web, API, Postgres, Valkey, MinIO; **without** `ai-agent`) behind HTTPS on a dedicated subdomain (exact hostname TBD at implement time, e.g. `paca.kaufman-ais.com`).

## Components

| Component | Role |
| --- | --- |
| Paca Web + API | Board, projects, tasks, documents, API keys |
| Postgres / Valkey / MinIO | Persistence, cache/queues, file/doc storage |
| `@paca-ai/paca-mcp` | Structured MCP tools for clients |
| Haystack | Production workflows (e.g. Document Intake → create/update Paca tasks + docs) |
| Onyx | End-user chat; may call Paca MCP tools when relevant |
| Cursor | Developer MCP client for smoke tests and manual board work |
| OpenAI | LLM only inside Onyx/Haystack |
| Witdem | First-class observability: traces + outcomes for Haystack/Onyx runs including Paca MCP tool calls |

## Data flows

### Phase 2 — MCP smoke (Cursor)

1. Operator creates Paca API key.  
2. Cursor MCP config points at internal/public Paca API URL + key.  
3. Agent creates a task and a doc; verifies read-back.

### Phase 3 — Intake → Paca (Haystack)

1. User message/file via Onyx (existing relevance gate).  
2. Haystack intake pipeline runs (classify, extract, Drive/Tasks as today where applicable).  
3. Pipeline calls Paca MCP (or thin MCP bridge) to create board task(s) and optionally a doc with summary/evidence.  
4. Confirmation returns to chat.  
5. Witdem records full run including Paca tool spans and outcome.

### Phase 4 — Agents as board members

Agents (via Haystack tools and/or Onyx tools, also usable from Cursor) claim issues, update status, comment, and write/update docs. Same MCP surface; Witdem measures those runs.

## Deployment notes

- Prefer official Paca release compose + install path on the VPS.  
- Start **without** built-in AI agent: `docker compose --env-file .env up -d --scale ai-agent=0` (or equivalent service name in the release compose).  
- TLS via host nginx/Caddy pattern consistent with existing Hostinger setup (`deploy-hostinger` in the Onyx/Witdem intake repo is the reference for DNS/certs style).  
- Secrets: JWT/DB/encryption keys for Paca; `PACA_API_KEY` only in client environments (Haystack, Onyx, Cursor local) — never committed.  
- Resource caution: even lean Paca adds Postgres/MinIO/Valkey; confirm VPS headroom before go-live.

## Error handling

- Paca or MCP unreachable → tool/workflow fails loudly; no silent drop of intake results.  
- Do not retry-storm MCP on hard 4xx auth errors; alert via Witdem failure outcome.  
- Partial success (e.g. Drive OK, Paca fail) must be visible in Witdem and in the user-facing confirmation.

## Testing / verification

1. Paca health + HTTPS login.  
2. Cursor MCP: create task + doc.  
3. Haystack workflow: intake-like path creates Paca task/doc; Witdem evidence shows nested tool spans + outcome.  
4. Onyx: tool smoke that hits Paca MCP.  
5. Failure injection: stop Paca API briefly; confirm controlled failure in Witdem.

## Delivery phases

1. **Paca lean on Hostinger** — compose, subdomain, TLS, admin login.  
2. **MCP** — Cursor first for verification, then wire Haystack + Onyx clients.  
3. **Intake → Paca** — tasks (+ docs) from Haystack workflows.  
4. **Board-member behaviour** — claim, status, comments, docs as routine agent work.

Implementation proceeds in that order even though this design covers all four.

## Open items (resolved in plan)

- Hostname: `paca.kaufman-ais.com` → `187.124.175.57`.  
- Haystack: Python REST `PacaClient` mirroring MCP task/doc ops; Cursor/Onyx use official MCP.  
- Intake field mapping: documented in plan Task 9 / `docs/intake-paca-mapping.md`.  
- Google Tasks: remain parallel (Paca additive).

## Related repos (do not merge)

- `onyx-witdem-document-intake` — existing Onyx/Haystack/Witdem Hostinger deploy  
- `witdem-oss` — Witdem product/SDK  
- `kaufman-ais-com` — marketing site (unrelated)  
- Upstream: [Paca-AI/paca](https://github.com/Paca-AI/paca)
