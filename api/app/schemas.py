from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str
    priority: str
    dueAt: Optional[datetime] = None
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default="normal")
    dueAt: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = None
    priority: Optional[str] = None
    dueAt: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskListResponse(BaseModel):
    items: list[Task]
    page: int
    size: int
    total: int
