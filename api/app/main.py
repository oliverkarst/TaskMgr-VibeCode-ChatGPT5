from datetime import datetime, timezone
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="open", pattern="^(open|doing|done)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    dueAt: Optional[datetime] = None
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default="normal", pattern="^(low|normal|high)$")
    dueAt: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, pattern="^(open|doing|done)$")
    priority: Optional[str] = Field(default=None, pattern="^(low|normal|high)$")
    dueAt: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskListResponse(BaseModel):
    items: List[Task]
    page: int
    size: int
    total: int

app = FastAPI(
    title="Tasks API",
    version="0.2.0",
    description="Step 2: In-Memory CRUD für Tasks",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

_TASKS: Dict[UUID, Task] = {}

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

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

@app.get("/api/v1/tasks", response_model=TaskListResponse, tags=["tasks"])
async def list_tasks(page: int = 1, size: int = 20, q: Optional[str] = None):
    if page < 1 or size < 1 or size > 100:
        raise problem(status.HTTP_400_BAD_REQUEST, "Bad Request", "Invalid pagination parameters")
    tasks = list(_TASKS.values())
    if q:
        q_lower = q.lower()
        tasks = [t for t in tasks if q_lower in t.title.lower() or (t.description and q_lower in t.description.lower())]
    total = len(tasks)
    start = (page - 1) * size
    end = start + size
    return TaskListResponse(items=tasks[start:end], page=page, size=size, total=total)

@app.post("/api/v1/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["tasks"])
async def create_task(payload: TaskCreate, response: Response):
    t = Task(
        id=uuid4(),
        title=payload.title,
        description=payload.description,
        status="open",
        priority=payload.priority or "normal",
        dueAt=payload.dueAt,
        tags=payload.tags or [],
        createdAt=now_utc(),
        updatedAt=now_utc(),
    )
    _TASKS[t.id] = t
    response.headers["Location"] = f"/api/v1/tasks/{t.id}"
    return t

@app.get("/api/v1/tasks/{id}", response_model=Task, tags=["tasks"])
async def get_task(id: UUID):
    t = _TASKS.get(id)
    if not t:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    return t

@app.patch("/api/v1/tasks/{id}", response_model=Task, tags=["tasks"])
async def update_task(id: UUID, payload: TaskUpdate):
    t = _TASKS.get(id)
    if not t:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    data = t.dict()
    updates = payload.dict(exclude_unset=True)
    for k, v in updates.items():
        data[k] = v
    data["updatedAt"] = now_utc()
    t2 = Task(**data)
    _TASKS[id] = t2
    return t2

@app.delete("/api/v1/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
async def delete_task(id: UUID):
    if id not in _TASKS:
        raise problem(status.HTTP_404_NOT_FOUND, "Not Found", "Task not found")
    _TASKS.pop(id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
