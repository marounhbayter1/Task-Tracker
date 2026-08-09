from fastapi import HTTPException, status

from app.models import TaskStatus


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status transition is allowed.

    Args:
        current (TaskStatus): The task's current status.
        new (TaskStatus): The requested new status.

    Returns:
        None: Returns nothing when the transition is allowed.

    Raises:
        HTTPException: 422 Unprocessable Entity if `(current, new)` is
            not a member of `VALID_TRANSITIONS`. Note this also
            covers a status transitioning to itself (e.g. ToDo ->
            ToDo), since same-to-same pairs are not in
            `VALID_TRANSITIONS`. The error `detail` includes the
            sorted list of allowed "From->To" transitions.
    """
    # Same -> same is invalid. Anything not in VALID_TRANSITIONS is invalid.
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to {new.value}. "
                f"Allowed transitions: {allowed}"
            ),
        )
