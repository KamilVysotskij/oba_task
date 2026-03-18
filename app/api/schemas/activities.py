from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    level: int


class ActivityTreeNode(BaseModel):
    id: int
    name: str
    level: int
    children: list[ActivityTreeNode] = Field(default_factory=list)


ActivityTreeNode.model_rebuild()
