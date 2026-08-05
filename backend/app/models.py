from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.tags import MAX_TAG_COUNT, MAX_TAG_LENGTH, normalize_tags


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = value.strip()

        if not title:
            raise ValueError("Title must not be blank")

        if len(title) > 200:
            raise ValueError("Title must be 200 characters or fewer")

        return title

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value

        return normalize_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError("Title must not be null")

        title = value.strip()

        if not title:
            raise ValueError("Title must not be blank")

        if len(title) > 200:
            raise ValueError("Title must be 200 characters or fewer")

        return title

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value

        return normalize_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime


class ActivityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    event_type: str
    message: str
    timestamp: datetime
