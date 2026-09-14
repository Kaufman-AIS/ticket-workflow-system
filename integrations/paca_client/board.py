"""Board-member helpers wrapping PacaClient task operations.

Claim uses the PATCH field ``assignee_id`` (not ``assignee``) so OpenAPI tools
and Haystack callers stay aligned with the Paca REST schema.
"""

from __future__ import annotations

from integrations.paca_client.client import PacaClient
from integrations.paca_client.models import Task


def claim_task(client: PacaClient, task_id: str, assignee_id: str) -> Task:
    """Assign ``task_id`` to ``assignee_id`` via ``update_task(..., assignee_id=...)``."""
    return client.update_task(task_id, assignee_id=assignee_id)


def set_status(client: PacaClient, task_id: str, status: str) -> Task:
    return client.update_task(task_id, status=status)


def add_comment(client: PacaClient, task_id: str, body: str) -> dict:
    return client.add_task_comment(task_id, body)
