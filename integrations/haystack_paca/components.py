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
