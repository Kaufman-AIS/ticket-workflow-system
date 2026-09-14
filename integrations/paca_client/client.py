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

    def add_task_comment(self, task_id: str, body: str) -> dict:
        return self._request("POST", f"/api/v1/tasks/{task_id}/comments", json={"body": body})

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
