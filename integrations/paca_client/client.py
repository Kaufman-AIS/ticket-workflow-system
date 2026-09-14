from __future__ import annotations

import httpx

from integrations.paca_client.blocknote import markdown_to_blocknote
from integrations.paca_client.models import Document, Task


class PacaError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class PacaClient:
    """HTTP client aligned with Paca v0.16 REST (same paths as @paca-ai/paca-mcp)."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self._base = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def _unwrap(self, payload: dict | list) -> dict | list:
        if isinstance(payload, dict) and "success" in payload:
            if not payload.get("success", True):
                raise PacaError(
                    f"Paca API error: {payload.get('error') or payload}",
                    status_code=None,
                )
            return payload.get("data", {})
        return payload

    def _request(self, method: str, path: str, **kwargs) -> dict | list:
        try:
            r = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as e:
            raise PacaError(f"transport error: {e}") from e
        if r.status_code >= 400:
            raise PacaError(f"Paca API {r.status_code}: {r.text[:500]}", status_code=r.status_code)
        if not r.content:
            return {}
        return self._unwrap(r.json())

    def create_task(self, project_id: str, title: str, description: str | None = None) -> Task:
        body: dict = {"title": title}
        if description:
            body["description"] = markdown_to_blocknote(description)
        else:
            body["description"] = None
        data = self._request("POST", f"/api/v1/projects/{project_id}/tasks", json=body)
        return Task.model_validate(data)

    def update_task(self, project_id: str, task_id: str, **fields) -> Task:
        body = dict(fields)
        if "description" in body and isinstance(body["description"], str):
            body["description"] = markdown_to_blocknote(body["description"])
        if "assignee_id" in body:
            assignee = body.pop("assignee_id")
            body["assignee_ids"] = [assignee] if assignee else []
        data = self._request("PATCH", f"/api/v1/projects/{project_id}/tasks/{task_id}", json=body)
        return Task.model_validate(data)

    def add_task_comment(self, project_id: str, task_id: str, body: str) -> dict:
        payload = {"content": markdown_to_blocknote(body)}
        data = self._request(
            "POST",
            f"/api/v1/projects/{project_id}/tasks/{task_id}/activities/comments",
            json=payload,
        )
        return data if isinstance(data, dict) else {"data": data}

    def list_tasks(self, project_id: str) -> list[Task]:
        data = self._request("GET", f"/api/v1/projects/{project_id}/tasks")
        if isinstance(data, list):
            items = data
        else:
            items = data.get("items", data.get("tasks", []))
        return [Task.model_validate(i) for i in items]

    def create_document(self, project_id: str, title: str, markdown: str) -> Document:
        body = {
            "title": title,
            "content": markdown_to_blocknote(markdown) if markdown else None,
        }
        data = self._request("POST", f"/api/v1/projects/{project_id}/docs", json=body)
        return Document.model_validate(data)

    def update_document(
        self,
        project_id: str,
        document_id: str,
        markdown: str | None = None,
        title: str | None = None,
    ) -> Document:
        body: dict = {}
        if markdown is not None:
            body["content"] = markdown_to_blocknote(markdown) if markdown else None
        if title is not None:
            body["title"] = title
        data = self._request(
            "PATCH",
            f"/api/v1/projects/{project_id}/docs/{document_id}",
            json=body,
        )
        return Document.model_validate(data)
