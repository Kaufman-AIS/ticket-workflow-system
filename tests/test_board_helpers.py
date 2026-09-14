import json

import pytest
from pytest_httpx import HTTPXMock

from integrations.paca_client import PacaClient
from integrations.paca_client.board import add_comment, claim_task, set_status


@pytest.fixture
def client():
    return PacaClient(base_url="https://paca.example", api_key="test-key")


def test_claim_task_patches_assignee_id(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/tasks/task-1",
        json={"id": "task-1", "title": "File invoice", "assignee_id": "user-42"},
    )
    out = claim_task(client, "task-1", assignee_id="user-42")
    assert out.id == "task-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"assignee_id": "user-42"}


def test_set_status_patches_status(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/tasks/task-1",
        json={"id": "task-1", "title": "File invoice", "status": "in_progress"},
    )
    out = set_status(client, "task-1", status="in_progress")
    assert out.id == "task-1"
    assert out.status == "in_progress"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"status": "in_progress"}


def test_add_comment_posts_body(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/tasks/task-1/comments",
        json={"id": "cmt-1", "body": "Claimed — starting intake"},
    )
    out = add_comment(client, "task-1", body="Claimed — starting intake")
    assert out == {"id": "cmt-1", "body": "Claimed — starting intake"}
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"body": "Claimed — starting intake"}
