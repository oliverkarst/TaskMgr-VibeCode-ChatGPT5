from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session

from .db import get_session
from . import models, schemas

app = FastAPI(
    title="Tasks API",
    version="0.3.3",
    description="Step 3 (fixed3): PostgreSQL Persistenz",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

def now_utc():
    return datetime.now(timezone.utc)

def to_schema(task: models.Task) -> schemas.Task:
    return schemas.Task(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value if hasattr(task.status, "value") else task.status,
        priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
        dueAt=task.due_at,
        tags=task.tags or [],
        createdAt=task.created_at,
        updatedAt=task.updated_at,
    )

def problem(status_code: int, title: str, detail: Optional[str] = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail={
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
    })

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "time": now_utc().isoformat()}

@app.get("/api/v1/tasks", response_model=schemas.TaskListResponse, tags=["tasks"])
def list_tasks(page: int = 1, size: int = 20, q: Optional[str] = None, db: Session = Depends(get_session)):
    if page < 1 or size < 1 or size > 100:
        raise problem(status.HTTP_400_BAD_REQUEST, "Bad Request", "Invalid pagination parameters")
    query = db.query(models.Task)
    if q:
        ilike = f"%{q}%"
        query = query.filter((models.Task.title.ilike(ilike)) | (models.Task.description.ilike(ilike)))
    total = query.count()
    items = (query
             .order_by(models.Task.created_at.desc())
             .offset((page - 1) * size)
             .limit(size)
             .all())
    return schemas.TaskListResponse(
        items=[to_schema(t) for t in items],
        page=page, size=size, total=total
    )

@app.post("/api/v1/tasks", response_model=schemas.Task, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: schemas.TaskCreate, response: Response, db: Session = Depends(get_session)):
    t = models.Task(
        title=payload.title,
        description=payload.description,
        status=models.StatusEnum.open,
        priority=models.PriorityEnum(payload.priority) if payload.priority else models.PriorityEnum.normal,
        due_at=payload.dueAt,
        tags=payload.tags or [],
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    response.headers["Location"] = f"/api/v1/tasks/{t.id}"
    return to_schema(t)

@app.get("/api/v1/tasks/{id}", response_model=schemas.Task, tags=["tasks"])
def get_task(id: UUID, db: Session = Depends(get_session)):
    t = db.get(models.Task, id)
    if not t:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    return to_schema(t)

@app.patch("/api/v1/tasks/{id}", response_model=schemas.Task, tags=["tasks"])
def update_task(id: UUID, payload: schemas.TaskUpdate, db: Session = Depends(get_session)):
    t = db.get(models.Task, id)
    if not t:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    data = payload.dict(exclude_unset=True)
    if "title" in data: t.title = data["title"]
    if "description" in data: t.description = data["description"]
    if "status" in data and data["status"] is not None: t.status = models.StatusEnum(data["status"])
    if "priority" in data and data["priority"] is not None: t.priority = models.PriorityEnum(data["priority"])
    if "dueAt" in data: t.due_at = data["dueAt"]
    if "tags" in data and data["tags"] is not None: t.tags = data["tags"]
    db.commit()
    db.refresh(t)
    return to_schema(t)

@app.delete("/api/v1/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(id: UUID, db: Session = Depends(get_session)):
    t = db.get(models.Task, id)
    if not t:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    db.delete(t)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
