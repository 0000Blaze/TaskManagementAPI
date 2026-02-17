from __future__ import annotations
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

def _strip_or_none(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v2 = v.strip()
    return v2 if v2 else None

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: int = Field(3, ge=1, le=5)
    due_date: Optional[date] = None
    tags: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must be non-empty")
        return v

    @field_validator("description")
    @classmethod
    def desc_strip(cls, v: Optional[str]) -> Optional[str]:
        return _strip_or_none(v)

    @field_validator("tags")
    @classmethod
    def tags_normalize(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        cleaned = []
        for t in v:
            t2 = t.strip()
            if not t2:
                continue
            cleaned.append(t2.lower())
        # de-duplicate while preserving order
        seen = set()
        out = []
        for t in cleaned:
            if t not in seen:
                out.append(t)
                seen.add(t)
        return out or []

    @field_validator("due_date")
    @classmethod
    def due_date_not_past(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        if v < date.today():
            raise ValueError("due_date must not be in the past")
        return v

class TaskCreate(TaskBase):
    pass

class TaskPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def patch_title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Title must be non-empty")
        return v

    @field_validator("description")
    @classmethod
    def patch_desc_strip(cls, v: Optional[str]) -> Optional[str]:
        return _strip_or_none(v)

    @field_validator("tags")
    @classmethod
    def patch_tags_normalize(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        cleaned = []
        for t in v:
            t2 = t.strip()
            if not t2:
                continue
            cleaned.append(t2.lower())
        seen = set()
        out = []
        for t in cleaned:
            if t not in seen:
                out.append(t)
                seen.add(t)
        return out or []

    @field_validator("due_date")
    @classmethod
    def patch_due_date_not_past(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        if v < date.today():
            raise ValueError("due_date must not be in the past")
        return v

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    priority: int
    due_date: Optional[date]
    completed: bool
    tags: List[str]

class PaginatedTasks(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TaskOut]
