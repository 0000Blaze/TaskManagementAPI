from datetime import datetime, date, timezone

def utcnow():
    return datetime.now(timezone.utc)

from sqlalchemy import (
    Table, Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_task_tags_task_id", "task_id"),
    Index("ix_task_tags_tag_id", "tag_id"),
)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tags = relationship("Tag", secondary=task_tags, back_populates="tasks", lazy="selectin")

    __table_args__ = (
        Index("ix_tasks_priority", "priority"),
        Index("ix_tasks_completed", "completed"),
        Index("ix_tasks_due_date", "due_date"),
        Index("ix_tasks_deleted_at", "deleted_at"),
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    tasks = relationship("Task", secondary=task_tags, back_populates="tags")

    __table_args__ = (
        UniqueConstraint("name", name="uq_tags_name"),
    )
