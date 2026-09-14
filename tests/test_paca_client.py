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
