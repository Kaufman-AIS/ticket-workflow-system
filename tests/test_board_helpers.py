import json

import pytest
from pytest_httpx import HTTPXMock

from integrations.paca_client import PacaClient
from integrations.paca_client.blocknote import markdown_to_blocknote
from integrations.paca_client.board import add_comment, claim_task, set_status


@pytest.fixture
def client():
    return PacaClient(base_url="https://paca.example", api_key="test-key")


def test_claim_task_patches_assignee_id(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/projects/proj-1/tasks/task-1",
        json={"success": True, "data": {"id": "task-1", "title": "File invoice"}},
    )
    out = claim_task(client, "proj-1", "task-1", assignee_id="user-42")
    assert out.id == "task-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"assignee_ids": ["user-42"]}


def test_set_status_patches_status_id(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="PATCH",
        url="https://paca.example/api/v1/projects/proj-1/tasks/task-1",
        json={"success": True, "data": {"id": "task-1", "title": "File invoice"}},
    )
    out = set_status(client, "proj-1", "task-1", status_id="status-todo")
    assert out.id == "task-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {"status_id": "status-todo"}


def test_add_comment_posts_blocknote(httpx_mock: HTTPXMock, client: PacaClient):
    httpx_mock.add_response(
        method="POST",
        url="https://paca.example/api/v1/projects/proj-1/tasks/task-1/activities/comments",
        json={"success": True, "data": {"id": "cmt-1"}},
    )
    out = add_comment(client, "proj-1", "task-1", body="Claimed — starting intake")
    assert out["id"] == "cmt-1"
    req = httpx_mock.get_request()
    assert json.loads(req.content) == {
        "content": markdown_to_blocknote("Claimed — starting intake")
    }
