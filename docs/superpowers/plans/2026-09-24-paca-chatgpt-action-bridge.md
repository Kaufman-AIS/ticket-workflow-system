# Paca ChatGPT Action Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the full installed Paca MCP tool set to a Custom GPT through a secure OpenAPI GPT Action that also works from iOS.

**Architecture:** Add a small JSON-RPC Action router to the existing Node gateway. It authenticates a separate `CHATGPT_ACTION_TOKEN`, forwards `{method, params}` to the local Streamable HTTP Paca MCP server, and returns the MCP result without exposing `PACA_API_KEY`. Serve a secret-free OpenAPI schema and setup README from the same gateway.

**Tech Stack:** Node 22, Express, `@modelcontextprotocol/sdk`, `node:test`, OpenAPI 3.1, Docker Compose.

---

### Task 1: Action bridge contract and tests

**Files:**
- Create: `deploy/chatgpt-mcp/chatgpt-action.mjs`
- Create: `deploy/chatgpt-mcp/test/chatgpt-action.test.mjs`

- [ ] **Step 1: Write failing tests** for missing/invalid Bearer authentication, malformed JSON-RPC, unknown tool rejection, and successful tool forwarding using a fake MCP client.
- [ ] **Step 2: Run the tests** with `node --test deploy/chatgpt-mcp/test/chatgpt-action.test.mjs`; confirm they fail because the router module does not exist.
- [ ] **Step 3: Implement the minimal action router** with constant-time token comparison, JSON-RPC error envelopes, method allowlisting from `client.listTools()`, and `client.callTool({name, arguments})` dispatch.
- [ ] **Step 4: Run the focused tests** and confirm all pass.
- [ ] **Step 5: Commit** `test: define Paca GPT Action bridge contract`.

### Task 2: Connect the router to the existing MCP server

**Files:**
- Modify: `deploy/chatgpt-mcp/gateway.mjs`
- Modify: `deploy/chatgpt-mcp/package.json`
- Modify: `deploy/chatgpt-mcp/.env.example`

- [ ] **Step 1: Add an MCP client factory** using the same SDK copy already resolved for the OAuth gateway and a `StreamableHTTPClientTransport` pointed at `http://127.0.0.1:8770/mcp`.
- [ ] **Step 2: Mount `POST /chatgpt/rpc`** before the existing MCP routes and require `CHATGPT_ACTION_TOKEN`.
- [ ] **Step 3: Mount `GET /chatgpt/health`** returning bridge status and upstream reachability without task data.
- [ ] **Step 4: Add `CHATGPT_ACTION_TOKEN` to `.env.example`** with a minimum-length requirement and keep it excluded by `.gitignore`.
- [ ] **Step 5: Run syntax checks and the focused tests**.
- [ ] **Step 6: Commit** `feat: expose Paca MCP tools as GPT Action RPC`.

### Task 3: Publish the OpenAPI schema and GPT instructions

**Files:**
- Create: `deploy/chatgpt-mcp/openapi.yaml`
- Create: `deploy/chatgpt-mcp/README-gpt-action.md`
- Modify: `deploy/chatgpt-mcp/gateway.mjs`

- [ ] **Step 1: Add a public `GET /chatgpt/openapi.yaml` route** with an OpenAPI 3.1 schema for `POST /chatgpt/rpc`, Bearer auth, JSON-RPC request/response envelopes, and an explicit description that `method` is one of the discovered Paca MCP tool names.
- [ ] **Step 2: Add a public `GET /chatgpt/README.md` route** that documents the Custom GPT setup, Bearer token placement, confirmation-before-delete rule, and example prompts.
- [ ] **Step 3: Add tests** proving both documents are public and contain the expected endpoint/auth declarations.
- [ ] **Step 4: Run all local Action bridge tests and `node --check`**.
- [ ] **Step 5: Commit** `feat: publish Paca GPT Action schema`.

### Task 4: Deploy and configure the GPT Action secret

**Files:**
- Modify on VPS only: `/opt/ticket-workflow-system/chatgpt-mcp/.env`

- [ ] **Step 1: Generate a new high-entropy `CHATGPT_ACTION_TOKEN`** on the VPS without printing it into logs or chat.
- [ ] **Step 2: Deploy the committed bridge files and restart `paca-chatgpt-mcp`**.
- [ ] **Step 3: Verify publicly:** OpenAPI returns 200, health returns 200, RPC without Bearer returns 401, and RPC with the secret can call the project-list tool.
- [ ] **Step 4: Provide the token to the user only as a local retrieval command** so it can be pasted into the GPT Action configuration; never display it in the assistant response.

### Task 5: End-to-end GPT Action verification

- [ ] **Step 1: Import `https://paca.kaufman-ais.com/chatgpt/openapi.yaml`** in the Custom GPT Action editor.
- [ ] **Step 2: Select API Key authentication with Bearer type** and paste the locally retrieved action token.
- [ ] **Step 3: Test project listing, task lookup, task creation, update, and deletion confirmation behavior in GPT Preview.**
- [ ] **Step 4: Record the live URLs and setup steps in `docs/chatgpt-mcp.md`** and commit the final documentation.
