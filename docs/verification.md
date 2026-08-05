# Verification

## Baseline Check
- Confirmed repository structure and project scope from `README.md` and workspace files.
- The backend is a Python FastAPI application with JSON-backed storage under `backend/data/tasks.json`.
- The frontend is a static `frontend/index.html` page that interacts with the backend API at `http://localhost:8000`.
- Baseline validation included running the full test suite once before writing this document.

## Backend Test Results
- Command run: `pytest -q`
- Result: `24 passed`
- Warnings: 3 warnings from FastAPI / Starlette deprecation notices.

Key verified tests:
- `test_create_task_with_tags_normalizes_and_returns_tags` confirms tags are normalized (trimmed) and returned in the response.
- `test_create_task_with_blank_tag_returns_422` confirms empty tags are rejected with `422`.
- `test_activity_endpoint_records_create_update_and_delete_events` confirms create/update/delete operations are recorded in activity history.
- `test_activity_endpoint_records_status_change_events` confirms status transitions generate status-change activity events.

## Manual Browser Checks
- Verified the frontend includes a task creation modal with a `Tags` input field and a `Filter by tag` input field.
- Verified the `Activity` panel is present, with an initial empty-state message `No activity yet.` and a status line showing panel state.
- Verified task cards render tags as chips using `.tag-chip` styling when tasks include tags.
- Verified the activity panel is updated by frontend code after successful task create/update/delete actions via `fetchActivity()`.
- Verified the tag filter logic is present in the frontend and filters tasks by matching tag text.

## Behavior Contract
### Before refactor
- The app provided basic task CRUD operations but did not reliably record activity events for create/update/delete/status changes.
- Tag input was not normalized or validated consistently, leaving open the possibility of blank or malformed tags.

### After refactor
- Task creation and updates now support an optional `tags` list.
- Tags are normalized by trimming whitespace and rejecting blank values.
- A maximum tag count is enforced to prevent overly large tag lists.
- Activity events are appended to the existing JSON-backed store for create, update, delete, and status-change actions.
- The `/activity` endpoint returns a list of events with `event_type`, `message`, and `timestamp`.
- The frontend renders tags as chips on task cards and shows recent activity in reverse chronological order.

## Break Test Evidence
- `test_create_task_with_blank_tag_returns_422`
  - This test acts as a break test for tag normalization and validation. If blank tags were allowed, this test would fail.
- `test_activity_endpoint_records_create_update_and_delete_events`
  - This test acts as a break test for activity logging. If activity events were not appended for create/update/delete, this test would fail.
- `test_activity_endpoint_records_status_change_events`
  - This test provides additional break-test coverage for status-change event recording.

> Evidence: the latest `pytest -q` run completed with `24 passed`, confirming the current implementation satisfies the verified contract and that the selected break tests are passing.