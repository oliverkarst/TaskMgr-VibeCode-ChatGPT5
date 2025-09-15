from __future__ import annotations
import enum
import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import String, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

class StatusEnum(str, enum.Enum):
    open = "open"
    doing = "doing"
    done = "done"

class PriorityEnum(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum, name="task_status"), default=StatusEnum.open, nullable=False)
    priority: Mapped[PriorityEnum] = mapped_column(Enum(PriorityEnum, name="task_priority"), default=PriorityEnum.normal, nullable=False)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
