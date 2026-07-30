import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def _load_tasks() -> dict[str, TaskResponse]:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not _DATA_FILE.exists():
        _DATA_FILE.write_text("[]\n", encoding="utf-8")
        return {}

    task_data = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    return {task["id"]: TaskResponse.model_validate(task) for task in task_data}


def _save_tasks() -> None:
    task_data = [task.model_dump(mode="json") for task in _tasks.values()]
    _DATA_FILE.write_text(json.dumps(task_data, indent=2) + "\n", encoding="utf-8")


_tasks: dict[str, TaskResponse] = _load_tasks()


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )
    
    _tasks[task.id] = task
    _save_tasks()
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

    updated_task = existing_task.model_copy(
        update={
            **changes,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    _tasks[task_id] = updated_task
    _save_tasks()
    return updated_task


def delete_task(task_id: str) -> bool:
    if task_id not in _tasks:
        return False

    del _tasks[task_id]
    _save_tasks()
    return True


def _reset() -> None:
    _tasks.clear()
    _save_tasks()
