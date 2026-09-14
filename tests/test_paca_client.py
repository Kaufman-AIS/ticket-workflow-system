import json

import pytest
from pytest_httpx import HTTPXMock

from integrations.paca_client import PacaClient, PacaError
from integrations.paca_client.blocknote import markdown_to_blocknote


@pytest.fixture
def client():
    return PacaClient(base_url="https://paca.example", api_key="test-key")


def test_create_task_posts_json(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/projects/proj-1/tasks",
        json={"success": True, "data": {"id": "task-1", "title": "File invoice"}},
    )
    out = client.create_task(project_id="proj-1", title="File invoice", description="ACME GmbH")
    assert out.id == "task-1"
    assert out.title == "File invoice"
    req = httpx_mock.get_request()
    assert req.headers["X-API-Key"] == "test-key"
    body = json.loads(req.content)
    assert body["title"] == "File invoice"
    assert body["description"] == markdown_to_blocknote("ACME GmbH")


def test_create_document_posts_markdown(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/projects/proj-1/docs",
        json={"success": True, "data": {"id": "doc-1", "title": "Intake summary"}},
    )
    out = client.create_document(project_id="proj-1", title="Intake summary", markdown="# Hello")
    assert out.id == "doc-1"
    req = httpx_mock.get_request()
    body = json.loads(req.content)
    assert body["title"] == "Intake summary"
    assert body["content"] == markdown_to_blocknote("# Hello")


def test_update_task_patches_fields(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/projects/proj-1/tasks/task-1",
        json={"success": True, "data": {"id": "task-1", "title": "File invoice", "status": "done"}},
    )
    out = client.update_task("proj-1", "task-1", status_id="status-done")
    assert out.id == "task-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"status_id": "status-done"}


def test_list_tasks_returns_tasks(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="GET",
        url="https://paca.example/api/v1/projects/proj-1/tasks",
        json={
            "success": True,
            "data": {
                "items": [
                    {"id": "task-1", "title": "File invoice"},
                    {"id": "task-2", "title": "Send reminder"},
                ]
            },
        },
    )
    out = client.list_tasks("proj-1")
    assert len(out) == 2
    assert out[0].id == "task-1"
    assert out[1].title == "Send reminder"


def test_update_document_patches_content(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/projects/proj-1/docs/doc-1",
        json={"success": True, "data": {"id": "doc-1", "title": "Intake summary"}},
    )
    out = client.update_document("proj-1", "doc-1", markdown="# Updated")
    assert out.id == "doc-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"content": markdown_to_blocknote("# Updated")}


def test_auth_error_raises_paca_error(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/projects/proj-1/tasks",
        status_code=401,
    )
    with pytest.raises(PacaError) as ei:
        client.create_task(project_id="proj-1", title="x")
    assert ei.value.status_code == 401
