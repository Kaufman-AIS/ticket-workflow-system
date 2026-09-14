from unittest.mock import MagicMock

from integrations.haystack_paca.components import CreatePacaDocument, CreatePacaTask
from integrations.paca_client import PacaError


def test_create_paca_task_calls_client_and_returns_id():
    client = MagicMock()
    client.create_task.return_value = MagicMock(id="task-9", title="Invoice")
    comp = CreatePacaTask(client=client, project_id="proj-1")
    result = comp.run(title="Invoice", description="from intake")
    assert result["task_id"] == "task-9"
    client.create_task.assert_called_once()


def test_create_paca_document_calls_client_and_returns_id():
    client = MagicMock()
    client.create_document.return_value = MagicMock(id="doc-3", title="Notes")
    comp = CreatePacaDocument(client=client, project_id="proj-1")
    result = comp.run(title="Notes", markdown="# Hello")
    assert result["document_id"] == "doc-3"
    assert result["error"] == ""
    client.create_document.assert_called_once_with("proj-1", title="Notes", markdown="# Hello")


def test_create_paca_task_paca_error_returns_error_string():
    client = MagicMock()
    client.create_task.side_effect = PacaError("API down", status_code=503)
    comp = CreatePacaTask(client=client, project_id="proj-1")
    result = comp.run(title="Invoice", description="from intake")
    assert result["task_id"] == ""
    assert result["error"]
    assert "API down" in result["error"]
