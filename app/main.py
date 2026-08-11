"""Application entry point for the Task Tracker API."""

from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status

from app import storage
from app.business_rules import validate_status_transition
from app.models import ActivityEvent, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Task Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict[str, str]:
    """Report basic service liveness information.

    Returns:
        dict[str, str]: A mapping with a static "status" of "ok" and the
            current UTC "timestamp" in ISO 8601 format.

    Example:
        GET /health -> {"status": "ok", "timestamp": "2026-08-09T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post(
    "/tasks",
    response_model=TaskResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and record a "create" activity event.

    Args:
        payload (TaskCreate): The task fields to create. `title` is
            required and is validated to be non-blank and at most 200
            characters (see `TaskCreate.validate_title`). `tags`, if
            provided, are normalized and validated by
            `TaskCreate.validate_tags`. Unknown fields are rejected
            because `TaskCreate` forbids extra fields.

    Returns:
        TaskResponse: The newly created task, including a generated
            `id` and `created_at`/`updated_at` timestamps.

    Raises:
        No exception is raised directly by this function. FastAPI
        returns 422 Unprocessable Entity before this function runs if
        `payload` fails pydantic validation (e.g. blank title, unknown
        field, invalid tag).

    Example:
        POST /tasks
        {"title": "Write tests", "priority": "High"}
        -> 201 Created with the created TaskResponse body.
    """
    return storage.add_task(payload)


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    tags=["tasks"],
)
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status and/or priority.

    Args:
        status (TaskStatus | None): If provided, only tasks with this
            exact status are returned. Defaults to None (no filter).
        priority (TaskPriority | None): If provided, only tasks with
            this exact priority are returned. Defaults to None (no
            filter). When both `status` and `priority` are given, both
            conditions must match (logical AND).

    Returns:
        list[TaskResponse]: Matching tasks, in the order returned by
            `storage.get_all_tasks` (task-store iteration order). An
            empty list if no tasks match or none exist.

    Example:
        GET /tasks?status=ToDo&priority=High
    """
    return storage.get_all_tasks(status=status, priority=priority)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    response_model_exclude_none=True,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by its id.

    Args:
        task_id (str): The id of the task to fetch.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 Not Found if no task with `task_id` exists.

    Example:
        GET /tasks/{task_id}
    """
    task = storage.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    return task


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    response_model_exclude_none=True,
    tags=["tasks"],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply a partial update to an existing task.

    Only fields explicitly present in the request body are changed;
    omitted fields are left untouched (see
    `storage.update_task`, which uses
    `payload.model_dump(exclude_unset=True)`). If `status` is included
    and is not None, the transition from the task's current status is
    validated via `validate_status_transition` before the update is
    applied. Verified behavior: sending `"description": null` resets
    the description to an empty string, and sending `"tags": null`
    leaves the existing tags unchanged rather than clearing them (see
    `storage.update_task`).

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): The fields to change. Fields omitted
            from the request body are left as-is.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 Not Found if no task with `task_id` exists.
        HTTPException: 422 Unprocessable Entity if `payload.status` is
            set and the transition from the task's current status is
            not one of the allowed transitions in
            `business_rules.VALID_TRANSITIONS` (this includes setting
            `status` to its current value).

    Example:
        PATCH /tasks/{task_id}
        {"status": "InProgress"}
    """
    existing_task = storage.get_task_by_id(task_id)

    if existing_task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    if payload.status is not None:
        validate_status_transition(existing_task.status, payload.status)

    task = storage.update_task(task_id, payload)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by id and record a "delete" activity event.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        None: On success, FastAPI responds with 204 No Content and an
            empty body.

    Raises:
        HTTPException: 404 Not Found if no task with `task_id` exists.

    Example:
        DELETE /tasks/{task_id} -> 204 No Content
    """
    deleted = storage.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )


@app.get("/activity", response_model=list[ActivityEvent], tags=["activity"])
def list_activity() -> list[ActivityEvent]:
    """List all recorded activity events across all tasks.

    Returns:
        list[ActivityEvent]: All activity events (event types observed
            in this codebase: "create", "update", "status_change",
            "delete"), in the order they were recorded. Empty list if
            no activity has been recorded.

    Example:
        GET /activity
    """
    return storage.get_activity_events()
