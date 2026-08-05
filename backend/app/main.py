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
    """Return a simple indication that the API is running."""
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
    return storage.get_all_tasks(status=status, priority=priority)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    response_model_exclude_none=True,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
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
    deleted = storage.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )


@app.get("/activity", response_model=list[ActivityEvent], tags=["activity"])
def list_activity() -> list[ActivityEvent]:
    return storage.get_activity_events()
