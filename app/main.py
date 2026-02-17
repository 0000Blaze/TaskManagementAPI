from __future__ import annotations
from fastapi import FastAPI, Depends, Query, Path, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db import get_db, engine, Base
from app import crud
from app.schemas import TaskCreate, TaskPatch, TaskOut, PaginatedTasks
from app.errors import to_error_payload, not_found_error

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {}
    for e in exc.errors():
        loc = e.get("loc", [])
        msg = e.get("msg", "Invalid value")
        # remove "body"/"query" prefix
        if loc and loc[0] in ("body", "query", "path"):
            loc = loc[1:]
        field = ".".join([str(x) for x in loc]) if loc else "unknown"
        details[field] = msg
    return JSONResponse(status_code=422, content={"error": "Validation Failed", "details": details})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=to_error_payload(exc.detail))

def _task_to_out(task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        completed=task.completed,
        tags=[t.name for t in task.tags] if task.tags else [],
    )

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = crud.create_task(
        db,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        tags=payload.tags,
    )
    return _task_to_out(task)

@app.get("/tasks", response_model=PaginatedTasks)
def list_tasks(
    completed: Optional[bool] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=5),
    tags: Optional[str] = Query(None, description="CSV list, e.g. work,urgent"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    tags_any: Optional[List[str]] = None
    if tags:
        tags_any = [t.strip().lower() for t in tags.split(",") if t.strip()]
    total, tasks = crud.list_tasks(
        db, completed=completed, priority=priority, tags_any=tags_any, limit=limit, offset=offset
    )
    return PaginatedTasks(
        total=total,
        limit=limit,
        offset=offset,
        items=[_task_to_out(t) for t in tasks],
    )

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise not_found_error(f"Task {task_id} not found")
    return _task_to_out(task)

@app.patch("/tasks/{task_id}", response_model=TaskOut)
def patch_task(task_id: int = Path(..., ge=1), payload: TaskPatch = None, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise not_found_error(f"Task {task_id} not found")

    data = payload.model_dump(exclude_unset=True)
    replace_tags = "tags" in data
    task = crud.update_task(
        db,
        task,
        title=data.get("title"),
        description=data.get("description"),
        priority=data.get("priority"),
        due_date=data.get("due_date"),
        completed=data.get("completed"),
        tags=data.get("tags"),
        replace_tags=replace_tags,
    )
    return _task_to_out(task)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise not_found_error(f"Task {task_id} not found")
    crud.soft_delete_task(db, task)
    return JSONResponse(status_code=204, content=None)
