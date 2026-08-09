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
        """Validate and normalize a task title.

        Args:
            value (str): The raw title supplied by the caller.

        Returns:
            str: The title with leading/trailing whitespace stripped.

        Raises:
            ValueError: If the stripped title is empty, or if it is
                longer than 200 characters. Pydantic turns this into a
                422 response when `TaskCreate` is used as a FastAPI
                request body.
        """
        title = value.strip()

        if not title:
            raise ValueError("Title must not be blank")

        if len(title) > 200:
            raise ValueError("Title must be 200 characters or fewer")

        return title

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize the `tags` list via `tags.normalize_tags`.

        Args:
            value (list[str] | None): The raw tags supplied by the
                caller, or None if the field was omitted.

        Returns:
            list[str] | None: None if `value` is None; otherwise the
                normalized tag list (whitespace-stripped, non-blank,
                at most `MAX_TAG_COUNT` tags of at most
                `MAX_TAG_LENGTH` characters each).

        Raises:
            ValueError: If any tag is not a string, is blank after
                stripping, exceeds `MAX_TAG_LENGTH`, or if more than
                `MAX_TAG_COUNT` tags are supplied (raised by
                `normalize_tags`). Pydantic turns this into a 422
                response when `TaskCreate` is used as a FastAPI
                request body.
        """
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
        """Validate and normalize a task title for a partial update.

        Because `title` defaults to None on `TaskUpdate` and pydantic
        does not run field validators on an unset default, this
        validator only runs when the caller explicitly includes
        `title` in the request body. [VERIFIED] Sending
        `"title": null` therefore reaches this validator and fails
        (rather than being treated as "no change"), while omitting
        `title` entirely skips validation and leaves the title
        unchanged.

        Args:
            value (str | None): The raw title supplied by the caller.

        Returns:
            str: The title with leading/trailing whitespace stripped.

        Raises:
            ValueError: If `value` is None, if the stripped title is
                empty, or if it is longer than 200 characters.
                Pydantic turns this into a 422 response when
                `TaskUpdate` is used as a FastAPI request body.
        """
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
        """Validate and normalize the `tags` list for a partial update.

        Args:
            value (list[str] | None): The raw tags supplied by the
                caller, or None if omitted or explicitly set to null.

        Returns:
            list[str] | None: None unchanged. [VERIFIED] Per
                `storage.update_task`, a None here is interpreted as
                "keep the task's existing tags" rather than "clear the
                tags". Otherwise, the normalized tag list produced by
                `normalize_tags`.

        Raises:
            ValueError: If any tag is not a string, is blank after
                stripping, exceeds `MAX_TAG_LENGTH`, or if more than
                `MAX_TAG_COUNT` tags are supplied (raised by
                `normalize_tags`). Pydantic turns this into a 422
                response when `TaskUpdate` is used as a FastAPI
                request body.
        """
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
