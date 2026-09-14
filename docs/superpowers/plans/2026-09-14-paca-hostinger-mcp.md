# Paca Hostinger MCP Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy lean Paca on the Hostinger VPS and connect Haystack, Cursor, and Onyx so agents can manage tickets and docs, with Witdem observing production runs.

**Architecture:** Official Paca Docker Compose without the built-in AI agent; TLS at `paca.kaufman-ais.com`. Cursor and Onyx use `@paca-ai/paca-mcp`. Haystack workflows use a Python HTTP client that mirrors MCP task/doc operations (reliable inside Python workers) and emit Witdem spans. Google Tasks remain in parallel for now.

**Tech Stack:** Paca (Docker), nginx/certbot, `@paca-ai/paca-mcp`, Python 3.11+, `httpx`, `witdem-sdk`, Haystack 3 components, pytest, GitHub Actions SSH deploy (same pattern as `onyx-witdem-document-intake`).

**Spec:** `docs/superpowers/specs/2026-09-14-paca-hostinger-mcp-design.md`

**Locked open items:**
- Hostname: `paca.kaufman-ais.com` → VPS `187.124.175.57`
- Host bind: `127.0.0.1:8090` → Paca HTTP (nginx terminates TLS)
- Haystack ↔ Paca: Python REST client (`integrations/paca_client`) matching MCP ops `create_task`, `update_task`, `create_document`, `update_document`, `list_tasks`
- Google Tasks: keep existing intake behaviour; Paca is additive

---

## File map

| Path | Responsibility |
| --- | --- |
| `deploy/paca/README.md` | How to fetch release compose + scale ai-agent to 0 |
| `deploy/paca/.env.example` | Required Paca env vars (no secrets) |
| `deploy/paca/docker-compose.override.yml` | Bind `127.0.0.1:8090:80`, scale ai-agent 0 |
| `deploy/nginx/paca.kaufman-ais.com.conf` | TLS reverse proxy to `:8090` |
| `docs/deploy-hostinger-paca.md` | DNS, certbot, first-boot checklist |
| `docs/cursor-mcp.md` | Cursor MCP JSON + smoke prompts |
| `docs/onyx-paca-tool.md` | Onyx tool wiring notes |
| `integrations/paca_client/__init__.py` | Public exports |
| `integrations/paca_client/client.py` | `PacaClient` HTTP wrapper |
| `integrations/paca_client/models.py` | Typed request/response models |
| `integrations/haystack_paca/components.py` | Haystack components wrapping client + Witdem |
| `integrations/haystack_paca/pipeline_snippet.py` | Example intake→Paca wiring |
| `tests/test_paca_client.py` | Client unit tests (httpx mock) |
| `tests/test_haystack_paca_components.py` | Component unit tests |
| `scripts/smoke_paca_health.sh` | HTTPS health + login page check |
| `scripts/smoke_paca_api.py` | Create task+doc via API key (CI/VPS) |
| `.github/workflows/deploy-paca.yml` | SSH deploy of compose/nginx artifacts |
| `pyproject.toml` | Package metadata + pytest deps |
| `.gitignore` | `.env`, secrets, `__pycache__` |

---

### Task 1: Repo scaffolding

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Modify: `README.md`
- Create: `integrations/paca_client/__init__.py`
- Create: `integrations/haystack_paca/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Add `.gitignore`**

```gitignore
.env
.env.*
!.env.example
deploy/paca/.env
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
.DS_Store
secrets/
*.pem
```

- [ ] **Step 2: Add `pyproject.toml`**

```toml
[project]
name = "ticket-workflow-system"
version = "0.1.0"
description = "Paca workflows on Hostinger with Haystack, Cursor, Onyx, Witdem"
requires-python = ">=3.11"
dependencies = [
  "httpx>=0.27",
  "pydantic>=2.0",
]

[project.optional-dependencies]
haystack = [
  "haystack-ai>=2.0",
  "witdem-sdk[haystack]>=0.1",
]
dev = [
  "pytest>=8.0",
  "pytest-httpx>=0.30",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 3: Replace `README.md` body** with links to spec, plan, and `docs/deploy-hostinger-paca.md` (keep short).

- [ ] **Step 4: Create empty package `__init__.py` files** listed above.

- [ ] **Step 5: Commit**

```bash
git add .gitignore pyproject.toml README.md integrations tests
git commit -m "chore: scaffold ticket-workflow-system package layout"
```

---

### Task 2: Paca deploy artifacts (lean)

**Files:**
- Create: `deploy/paca/README.md`
- Create: `deploy/paca/.env.example`
- Create: `deploy/paca/docker-compose.override.yml`
- Create: `deploy/nginx/paca.kaufman-ais.com.conf`
- Create: `docs/deploy-hostinger-paca.md`

- [ ] **Step 1: Write `deploy/paca/.env.example`**

```bash
# Copy to .env on the VPS — generate secrets with: openssl rand -hex 32
PUBLIC_URL=https://paca.kaufman-ais.com
JWT_SECRET=
ADMIN_PASSWORD=
POSTGRES_PASSWORD=
AGENT_API_KEY=
INTERNAL_API_KEY=
ENCRYPTION_KEY=
```

- [ ] **Step 2: Write `deploy/paca/docker-compose.override.yml`**

```yaml
# Used with the official release compose from:
# https://github.com/Paca-AI/paca/releases/latest/download/docker-compose.yml
services:
  # Exact gateway service name may be `caddy`, `nginx`, or `web` depending on
  # release — adjust ports mapping to the service that listens on :80.
  caddy:
    ports:
      - "127.0.0.1:8090:80"
  ai-agent:
    deploy:
      replicas: 0
```

If the release compose uses a different gateway service name, document the rename in `deploy/paca/README.md` after downloading the file once during Task 3 dry-run.

- [ ] **Step 3: Write `deploy/nginx/paca.kaufman-ais.com.conf`** (mirror Onyx template)

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name paca.kaufman-ais.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name paca.kaufman-ais.com;

    ssl_certificate     /etc/letsencrypt/live/paca.kaufman-ais.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/paca.kaufman-ais.com/privkey.pem;

    client_max_body_size 50m;

    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

- [ ] **Step 4: Write `deploy/paca/README.md` and `docs/deploy-hostinger-paca.md`**

`docs/deploy-hostinger-paca.md` must include:

1. DNS: `paca.kaufman-ais.com` A → `187.124.175.57`
2. On VPS: `mkdir -p /opt/ticket-workflow-system/paca && cd …`
3. Download release compose + Caddyfile/nginx assets from Paca latest release
4. Copy `.env.example` → `.env`, fill secrets
5. `docker compose -f docker-compose.yml -f docker-compose.override.yml --env-file .env up -d --scale ai-agent=0`
6. Install nginx site + `certbot --nginx -d paca.kaufman-ais.com`
7. Verify: `curl -fsS https://paca.kaufman-ais.com/` returns 200/302 HTML
8. Create API key in Paca UI (Settings → API Keys)

- [ ] **Step 5: Commit**

```bash
git add deploy docs/deploy-hostinger-paca.md
git commit -m "docs: add lean Paca Hostinger deploy artifacts"
```

---

### Task 3: Health smoke script

**Files:**
- Create: `scripts/smoke_paca_health.sh`
- Test: run script against a URL (local mock or production after deploy)

- [ ] **Step 1: Write `scripts/smoke_paca_health.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-https://paca.kaufman-ais.com}"
code=$(curl -sS -o /tmp/paca_smoke_body.html -w "%{http_code}" "$BASE_URL/")
echo "HTTP $code for $BASE_URL/"
test "$code" = "200" -o "$code" = "302" -o "$code" = "301"
grep -qi "html\|paca\|login\|sign" /tmp/paca_smoke_body.html
echo "OK health smoke"
```

- [ ] **Step 2: Make executable and dry-run expectation**

```bash
chmod +x scripts/smoke_paca_health.sh
# Before DNS/deploy this will fail — that is expected until Task 7.
# After deploy:
# ./scripts/smoke_paca_health.sh https://paca.kaufman-ais.com
# Expected: OK health smoke
```

- [ ] **Step 3: Commit**

```bash
git add scripts/smoke_paca_health.sh
git commit -m "chore: add Paca HTTPS health smoke script"
```

---

### Task 4: `PacaClient` + unit tests (TDD)

**Files:**
- Create: `integrations/paca_client/models.py`
- Create: `integrations/paca_client/client.py`
- Create: `tests/test_paca_client.py`
- Modify: `integrations/paca_client/__init__.py`

- [ ] **Step 1: Write failing tests in `tests/test_paca_client.py`**

```python
import httpx
import pytest
from pytest_httpx import HTTPXMock

from integrations.paca_client import PacaClient, PacaError


@pytest.fixture
def client():
    return PacaClient(base_url="https://paca.example", api_key="test-key")


def test_create_task_posts_json(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/tasks",
        json={"id": "task-1", "title": "File invoice"},
    )
    out = client.create_task(project_id="proj-1", title="File invoice", description="ACME GmbH")
    assert out.id == "task-1"
    assert out.title == "File invoice"
    req = httpx_mock.get_request()
    assert req.headers["Authorization"] == "Bearer test-key"


def test_create_document_posts_markdown(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/documents",
        json={"id": "doc-1", "title": "Intake summary"},
    )
    out = client.create_document(project_id="proj-1", title="Intake summary", markdown="# Hello")
    assert out.id == "doc-1"


def test_auth_error_raises_paca_error(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(method="POST", url="https://paca.example/api/v1/tasks", status_code=401)
    with pytest.raises(PacaError) as ei:
        client.create_task(project_id="proj-1", title="x")
    assert ei.value.status_code == 401
```

> **API path note:** Confirm exact REST paths against the live Paca OpenAPI/`/api` docs after Task 7. If paths differ (e.g. `/api/tasks`), update `client.py` and these tests in the same commit — do not invent a second client.

- [ ] **Step 2: Run tests — expect fail**

```bash
python -m pip install -e ".[dev]"
pytest tests/test_paca_client.py -v
```

Expected: `ImportError` or `PacaClient` missing.

- [ ] **Step 3: Implement models + client**

`integrations/paca_client/models.py`:

```python
from pydantic import BaseModel


class Task(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str | None = None


class Document(BaseModel):
    id: str
    title: str
```

`integrations/paca_client/client.py`:

```python
from __future__ import annotations

import httpx

from integrations.paca_client.models import Document, Task


class PacaError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class PacaClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self._base = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            r = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as e:
            raise PacaError(f"transport error: {e}") from e
        if r.status_code >= 400:
            raise PacaError(f"Paca API {r.status_code}: {r.text[:500]}", status_code=r.status_code)
        if not r.content:
            return {}
        return r.json()

    def create_task(self, project_id: str, title: str, description: str | None = None) -> Task:
        data = self._request(
            "POST",
            "/api/v1/tasks",
            json={"project_id": project_id, "title": title, "description": description},
        )
        return Task.model_validate(data)

    def update_task(self, task_id: str, **fields) -> Task:
        data = self._request("PATCH", f"/api/v1/tasks/{task_id}", json=fields)
        return Task.model_validate(data)

    def list_tasks(self, project_id: str) -> list[Task]:
        data = self._request("GET", "/api/v1/tasks", params={"project_id": project_id})
        items = data if isinstance(data, list) else data.get("items", data.get("tasks", []))
        return [Task.model_validate(i) for i in items]

    def create_document(self, project_id: str, title: str, markdown: str) -> Document:
        data = self._request(
            "POST",
            "/api/v1/documents",
            json={"project_id": project_id, "title": title, "content": markdown},
        )
        return Document.model_validate(data)

    def update_document(self, document_id: str, markdown: str | None = None, title: str | None = None) -> Document:
        body = {}
        if markdown is not None:
            body["content"] = markdown
        if title is not None:
            body["title"] = title
        data = self._request("PATCH", f"/api/v1/documents/{document_id}", json=body)
        return Document.model_validate(data)
```

Export `PacaClient`, `PacaError`, `Task`, `Document` from `__init__.py`.

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/test_paca_client.py -v
```

Expected: all PASS (adjust paths if live OpenAPI differs — update tests+client together).

- [ ] **Step 5: Commit**

```bash
git add integrations/paca_client tests/test_paca_client.py pyproject.toml
git commit -m "feat: add Paca HTTP client with unit tests"
```

---

### Task 5: Haystack components + Witdem spans

**Files:**
- Create: `integrations/haystack_paca/components.py`
- Create: `integrations/haystack_paca/pipeline_snippet.py`
- Create: `tests/test_haystack_paca_components.py`

- [ ] **Step 1: Write failing test**

```python
from unittest.mock import MagicMock

from integrations.haystack_paca.components import CreatePacaTask


def test_create_paca_task_calls_client_and_returns_id():
    client = MagicMock()
    client.create_task.return_value = MagicMock(id="task-9", title="Invoice")
    comp = CreatePacaTask(client=client, project_id="proj-1")
    result = comp.run(title="Invoice", description="from intake")
    assert result["task_id"] == "task-9"
    client.create_task.assert_called_once()
```

- [ ] **Step 2: Run — expect fail**

```bash
pytest tests/test_haystack_paca_components.py -v
```

- [ ] **Step 3: Implement components**

```python
from __future__ import annotations

from haystack import component

from integrations.paca_client import PacaClient, PacaError


@component
class CreatePacaTask:
    def __init__(self, client: PacaClient, project_id: str):
        self._client = client
        self._project_id = project_id

    @component.output_types(task_id=str, title=str, error=str)
    def run(self, title: str, description: str = "") -> dict:
        try:
            task = self._client.create_task(self._project_id, title=title, description=description or None)
            return {"task_id": task.id, "title": task.title, "error": ""}
        except PacaError as e:
            # Loud failure for Witdem / caller — do not swallow
            return {"task_id": "", "title": title, "error": str(e)}


@component
class CreatePacaDocument:
    def __init__(self, client: PacaClient, project_id: str):
        self._client = client
        self._project_id = project_id

    @component.output_types(document_id=str, error=str)
    def run(self, title: str, markdown: str) -> dict:
        try:
            doc = self._client.create_document(self._project_id, title=title, markdown=markdown)
            return {"document_id": doc.id, "error": ""}
        except PacaError as e:
            return {"document_id": "", "error": str(e)}
```

In `pipeline_snippet.py`, document wiring into existing intake (pseudo-pipeline comments only — actual merge happens in `onyx-witdem-document-intake` in Task 9): call `CreatePacaTask` then `CreatePacaDocument` after extract; if `error` non-empty, set Witdem outcome failed and include error in chat confirmation.

Instrument with Witdem using the project’s existing pattern from `onyx-witdem-document-intake` (import `witdem_sdk.integrations.haystack.instrument` at app entry — do not re-implement SDK).

- [ ] **Step 4: Run tests**

```bash
python -m pip install -e ".[dev,haystack]"
pytest tests/test_haystack_paca_components.py -v
```

Expected: PASS (skip or mark if haystack import heavy — prefer real import).

- [ ] **Step 5: Commit**

```bash
git add integrations/haystack_paca tests/test_haystack_paca_components.py
git commit -m "feat: add Haystack Paca task/doc components"
```

---

### Task 6: Cursor + Onyx MCP docs and API smoke

**Files:**
- Create: `docs/cursor-mcp.md`
- Create: `docs/onyx-paca-tool.md`
- Create: `scripts/smoke_paca_api.py`
- Create: `config/cursor-mcp.example.json`

- [ ] **Step 1: Write `config/cursor-mcp.example.json`**

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

- [ ] **Step 2: Write `docs/cursor-mcp.md`** — steps to merge into Cursor MCP settings; smoke prompts: list projects, create task, create document with markdown.

- [ ] **Step 3: Write `docs/onyx-paca-tool.md`** — Onyx custom tool that either (a) exposes OpenAPI wrapping `PacaClient` HTTP service, or (b) documents MCP if Onyx MCP support is enabled; prefer OpenAPI tool calling a tiny FastAPI sidecar later if needed. For v1: document using the same API key + `PacaClient` endpoints from an Onyx OpenAPI tool definition pointing at an internal helper URL (to be added when Onyx wiring lands in Task 10).

- [ ] **Step 4: Write `scripts/smoke_paca_api.py`**

```python
#!/usr/bin/env python3
"""Create a task and doc via PacaClient. Env: PACA_API_URL, PACA_API_KEY, PACA_PROJECT_ID."""
import os
import sys
from integrations.paca_client import PacaClient, PacaError

def main() -> int:
    base = os.environ["PACA_API_URL"]
    key = os.environ["PACA_API_KEY"]
    project = os.environ["PACA_PROJECT_ID"]
    client = PacaClient(base, key)
    try:
        task = client.create_task(project, title="smoke-task", description="api smoke")
        doc = client.create_document(project, title="smoke-doc", markdown="# smoke\n")
        print(f"OK task={task.id} doc={doc.id}")
        return 0
    except PacaError as e:
        print(f"FAIL {e}", file=sys.stderr)
        return 1
    finally:
        client.close()

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Commit**

```bash
git add docs/cursor-mcp.md docs/onyx-paca-tool.md config scripts/smoke_paca_api.py
git commit -m "docs: Cursor MCP and Paca API smoke helpers"
```

---

### Task 7: Hostinger go-live (manual + checklist)

**Files:**
- Modify: `docs/deploy-hostinger-paca.md` (checkboxes for executed steps)
- No app code

- [ ] **Step 1: DNS** — create `paca.kaufman-ais.com` A record → `187.124.175.57`; verify `dig +short paca.kaufman-ais.com`.

- [ ] **Step 2: On VPS** — follow `docs/deploy-hostinger-paca.md` to install lean Paca, nginx, certbot.

- [ ] **Step 3: Align REST paths** — open Paca API docs on the live instance; if `/api/v1/tasks` differs, fix `integrations/paca_client/client.py` + tests and commit `fix: align PacaClient paths to live OpenAPI`.

- [ ] **Step 4: Verify**

```bash
./scripts/smoke_paca_health.sh https://paca.kaufman-ais.com
# Expected: OK health smoke
```

Login as admin in browser; create a project; create API key; store key in a password manager / GitHub secret `PACA_API_KEY` (never commit).

- [ ] **Step 5: Commit any path fixes + checklist notes**

```bash
git add integrations/paca_client tests docs/deploy-hostinger-paca.md
git commit -m "fix: align Paca client with live API after Hostinger deploy"
```

---

### Task 8: Cursor MCP verification

**Files:** none (operator config)

- [ ] **Step 1: Add MCP server** from `config/cursor-mcp.example.json` with real key + `https://paca.kaufman-ais.com`.

- [ ] **Step 2: In Cursor Agent**, ask: list projects; create task “cursor-smoke”; create doc “cursor-smoke-doc” with short markdown.

- [ ] **Step 3: Confirm in Paca UI** that task and doc exist.

- [ ] **Step 4: Record evidence** in `docs/verification-log.md` (create file) with date and results; commit.

```bash
git add docs/verification-log.md
git commit -m "docs: record Cursor MCP smoke verification"
```

---

### Task 9: Wire Haystack intake → Paca (cross-repo)

**Files (this repo):**
- Modify: `integrations/haystack_paca/pipeline_snippet.py` with exact component graph
- Create: `docs/intake-paca-mapping.md`

**Files (`onyx-witdem-document-intake` — separate PR):**
- Add dependency on ticket-workflow-system client or vendored copy of `PacaClient` + components
- Call CreatePacaTask + CreatePacaDocument after successful extract
- Ensure Witdem instrumentation already wraps the pipeline; assert `error` fields surface as failed outcome

- [ ] **Step 1: Write `docs/intake-paca-mapping.md`**

| Intake field | Paca |
| --- | --- |
| document type + issuer | task title prefix e.g. `[invoice] ACME` |
| extracted summary | task description |
| full extract JSON / markdown | document body |
| Drive file link (if any) | append to task description |
| Google Tasks | unchanged (parallel) |

- [ ] **Step 2: Implement wiring in intake repo** (follow that repo’s TDD/patterns); env `PACA_API_URL`, `PACA_API_KEY`, `PACA_PROJECT_ID`.

- [ ] **Step 3: Run one intake** on staging/prod; confirm Paca task+doc; open Witdem run and verify spans include Paca HTTP / component work and outcome success|failure.

- [ ] **Step 4: Commit in both repos** with messages referencing each other.

---

### Task 10: Onyx tool smoke + board-member helpers

**Files:**
- Create: `integrations/paca_client/board.py` — helpers `claim_task`, `set_status`, `add_comment` wrapping client methods once API paths confirmed
- Create: `tests/test_board_helpers.py`
- Update: `docs/onyx-paca-tool.md` with OpenAPI snippet for 3 tools

- [ ] **Step 1: Failing tests for `claim_task` / `set_status`** (httpx mock PATCH).

- [ ] **Step 2: Implement helpers; tests pass.**

- [ ] **Step 3: Register Onyx tools** (or persona instructions) per `docs/onyx-paca-tool.md` on the VPS.

- [ ] **Step 4: Onyx chat smoke** — “create a Paca task titled onyx-smoke”; verify UI + Witdem turn if proxy records it.

- [ ] **Step 5: Commit**

```bash
git add integrations/paca_client/board.py tests/test_board_helpers.py docs/onyx-paca-tool.md
git commit -m "feat: board-member helpers and Onyx tool docs"
```

---

### Task 11: Failure injection + deploy workflow

**Files:**
- Create: `.github/workflows/deploy-paca.yml`
- Create: `docs/failure-injection.md`

- [ ] **Step 1: Document failure injection** — briefly stop Paca API container; run intake; expect non-empty `error` from component, Witdem failed outcome, user-visible failure; start container again.

- [ ] **Step 2: Add GitHub Actions workflow** mirroring `onyx-witdem-document-intake` SSH deploy: checkout, rsync/scp `deploy/` to `/opt/ticket-workflow-system`, remote `docker compose … up -d --scale ai-agent=0`. Secrets: `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`.

- [ ] **Step 3: Run failure injection once; log in `docs/verification-log.md`.**

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/deploy-paca.yml docs/failure-injection.md docs/verification-log.md
git commit -m "ci: Paca deploy workflow and failure-injection notes"
```

---

## Spec coverage checklist

| Spec requirement | Task |
| --- | --- |
| Lean Paca on Hostinger, no built-in agent | 2, 7 |
| HTTPS subdomain | 2, 7 |
| MCP Cursor | 6, 8 |
| Haystack workflows → tasks/docs | 4, 5, 9 |
| Onyx client | 6, 10 |
| Witdem first-class | 5, 9, 11 |
| OpenAI only via existing agents | (non-goal enforced — no Paca LLM config tasks) |
| Agents as board members | 10 |
| Loud MCP/API failures | 4, 5, 11 |
| Phased delivery order | Tasks ordered 1→11 |

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-14-paca-hostinger-mcp.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute in this session with executing-plans checkpoints  

Which approach?
