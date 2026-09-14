from pydantic import BaseModel


class Task(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str | None = None


class Document(BaseModel):
    id: str
    title: str
