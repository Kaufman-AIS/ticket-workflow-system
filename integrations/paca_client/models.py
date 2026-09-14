from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    description: Any | None = None
    status: str | None = None
    status_id: str | None = None
    project_id: str | None = None


class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    content: Any | None = None
    project_id: str | None = None
