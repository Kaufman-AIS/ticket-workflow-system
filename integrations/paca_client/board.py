"""Board-member helpers wrapping PacaClient task operations.

Claim maps to ``assignee_ids`` via ``assignee_id`` on ``update_task``.
Status updates use ``status_id`` (Paca status UUIDs, not free-form names).
"""

from __future__ import annotations

from integrations.paca_client.client import PacaClient
from integrations.paca_client.models import Task


def claim_task(client: PacaClient, project_id: str, task_id: str, assignee_id: str) -> Task:
    return client.update_task(project_id, task_id, assignee_id=assignee_id)


def set_status(client: PacaClient, project_id: str, task_id: str, status_id: str) -> Task:
    return client.update_task(project_id, task_id, status_id=status_id)


def add_comment(client: PacaClient, project_id: str, task_id: str, body: str) -> dict:
    return client.add_task_comment(project_id, task_id, body)
