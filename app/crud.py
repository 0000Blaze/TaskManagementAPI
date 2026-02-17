from __future__ import annotations
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct
from app.models import Task, Tag, task_tags
from datetime import datetime

def _get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    if not tag_names:
        return []
    existing = db.execute(select(Tag).where(Tag.name.in_(tag_names))).scalars().all()
    existing_map = {t.name: t for t in existing}
    to_create = [name for name in tag_names if name not in existing_map]
    for name in to_create:
        t = Tag(name=name)
        db.add(t)
        db.flush()  # obtain id
        existing_map[name] = t
    return [existing_map[name] for name in tag_names]

def create_task(db: Session, *, title: str, description: Optional[str], priority: int, due_date, tags: Optional[List[str]]):
    task = Task(title=title, description=description, priority=priority, due_date=due_date)
    if tags is not None:
        task.tags = _get_or_create_tags(db, tags)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_id: int) -> Optional[Task]:
    stmt = select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
    return db.execute(stmt).scalars().first()

def list_tasks(
    db: Session,
    *,
    completed: Optional[bool],
    priority: Optional[int],
    tags_any: Optional[List[str]],
    limit: int,
    offset: int
) -> Tuple[int, List[Task]]:
    base = select(Task).where(Task.deleted_at.is_(None))
    if completed is not None:
        base = base.where(Task.completed == completed)
    if priority is not None:
        base = base.where(Task.priority == priority)

    if tags_any:
        # Join to tags, match any name in list
        base = base.join(task_tags, Task.id == task_tags.c.task_id).join(Tag, Tag.id == task_tags.c.tag_id).where(Tag.name.in_(tags_any))

    # total count
    # count_stmt = select(func.count(distinct(Task.id))).select_from(base.subquery())
    subq = base.with_only_columns(Task.id).distinct().subquery()
    count_stmt = select(func.count()).select_from(subq)

    total = db.execute(count_stmt).scalar_one()

    # items
    items_stmt = base.distinct().order_by(Task.id).limit(limit).offset(offset)
    items = db.execute(items_stmt).scalars().all()
    return total, items

def update_task(
    db: Session,
    task: Task,
    *,
    title=None,
    description=None,
    priority=None,
    due_date=None,
    completed=None,
    tags=None,
    replace_tags: bool = False
):
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if priority is not None:
        task.priority = priority
    if due_date is not None:
        task.due_date = due_date
    if completed is not None:
        task.completed = completed

    if replace_tags and tags is not None:
        task.tags = _get_or_create_tags(db, tags)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def soft_delete_task(db: Session, task: Task):
    task.deleted_at = datetime.utcnow()
    db.add(task)
    db.commit()
