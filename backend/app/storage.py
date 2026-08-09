import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .models import ActivityEvent, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def _load_state() -> tuple[dict[str, TaskResponse], list[ActivityEvent]]:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not _DATA_FILE.exists():
        _DATA_FILE.write_text('{"tasks": [], "activity": []}\n', encoding="utf-8")
        return {}, []

    raw_data = json.loads(_DATA_FILE.read_text(encoding="utf-8"))

    if isinstance(raw_data, list):
        task_data = raw_data
        activity_data: list[dict] = []
    elif isinstance(raw_data, dict):
        task_data = raw_data.get("tasks", [])
        activity_data = raw_data.get("activity", [])
    else:
        task_data = []
        activity_data = []

    tasks = {task["id"]: TaskResponse.model_validate(task) for task in task_data}
    activity = [ActivityEvent.model_validate(event) for event in activity_data]
    return tasks, activity


def _save_state() -> None:
    task_data = [task.model_dump(mode="json") for task in _tasks.values()]
    activity_data = [event.model_dump(mode="json") for event in _activity_events]
    _DATA_FILE.write_text(
        json.dumps({"tasks": task_data, "activity": activity_data}, indent=2) + "\n",
        encoding="utf-8",
    )


_tasks: dict[str, TaskResponse]
_activity_events: list[ActivityEvent]
_tasks, _activity_events = _load_state()


def _append_activity(task_id: str, event_type: str, message: str) -> None:
    _activity_events.append(
        ActivityEvent(
            id=str(uuid4()),
            task_id=task_id,
            event_type=event_type,
            message=message,
            timestamp=datetime.now(timezone.utc),
        )
    )


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task, then record a "create" activity event.

    Args:
        payload (TaskCreate): The already-validated task data to
            store.

    Returns:
        TaskResponse: The newly created task, with a generated `id`
            and `created_at`/`updated_at` both set to the current UTC
            time.
    """
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )

    _tasks[task.id] = task
    _append_activity(task.id, "create", "Task created")
    _save_state()
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
) -> list[TaskResponse]:
    """Return tasks, optionally filtered by status and/or priority.

    Args:
        status (TaskStatus | None): If given, only include tasks with
            this exact status. Defaults to None (no filter).
        priority (TaskPriority | None): If given, only include tasks
            with this exact priority. Defaults to None (no filter).
            Both filters apply together (logical AND) when both are
            given.

    Returns:
        list[TaskResponse]: Matching tasks, in the in-memory task
            store's iteration (insertion) order.
    """
    tasks = list(_tasks.values())

    if status is not None:
        tasks = [task for task in tasks if task.status == status]

    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]

    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by id.

    Args:
        task_id (str): The id of the task to fetch.

    Returns:
        TaskResponse | None: The matching task, or None if no task
            with `task_id` exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task and persist it.

    Only fields explicitly set on `payload` are applied
    (`payload.model_dump(exclude_unset=True)`); every other field
    keeps its current value. [VERIFIED] An explicit
    `description=None` is normalized to an empty string, and an
    explicit `tags=None` leaves the existing tags unchanged (it does
    not clear them). A "status_change" activity event is recorded
    when `status` is among the changed fields and differs from the
    task's current status; otherwise, if any field changed, an
    "update" event is recorded.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): The fields to change.

    Returns:
        TaskResponse | None: The updated task, or None if no task
            with `task_id` exists. If `payload` has no fields set,
            the existing task is returned unchanged and no activity
            event is recorded.
    """
    existing_task = _tasks.get(task_id)

    if existing_task is None:
        return None

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        return existing_task

    if "description" in changes and changes["description"] is None:
        changes["description"] = ""

    if "tags" in changes and changes["tags"] is None:
        changes["tags"] = existing_task.tags

    updated_task = existing_task.model_copy(
        update={
            **changes,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    _tasks[task_id] = updated_task

    if "status" in changes and changes["status"] is not None:
        if existing_task.status != changes["status"]:
            _append_activity(task_id, "status_change", f"Status changed to {changes['status'].value}")
    else:
        _append_activity(task_id, "update", "Task updated")

    _save_state()
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a task by id and record a "delete" activity event.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        bool: True if a task was found and deleted, False if no task
            with `task_id` existed (in which case no activity event
            is recorded).
    """
    if task_id not in _tasks:
        return False

    del _tasks[task_id]
    _append_activity(task_id, "delete", "Task deleted")
    _save_state()
    return True


def get_activity_events() -> list[ActivityEvent]:
    """Return all recorded activity events, in the order recorded.

    Returns:
        list[ActivityEvent]: A new list containing every activity
            event currently stored (empty if none have been
            recorded).
    """
    return list(_activity_events)


def _reset() -> None:
    _tasks.clear()
    _activity_events.clear()
    _save_state()
