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
    tasks = list(_tasks.values())

    if status is not None:
        tasks = [task for task in tasks if task.status == status]

    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]

    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
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
    if task_id not in _tasks:
        return False

    del _tasks[task_id]
    _append_activity(task_id, "delete", "Task deleted")
    _save_state()
    return True


def get_activity_events() -> list[ActivityEvent]:
    return list(_activity_events)


def _reset() -> None:
    _tasks.clear()
    _activity_events.clear()
    _save_state()
