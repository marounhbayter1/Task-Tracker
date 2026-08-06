# Verification

## Baseline Check
- Confirmed that the repository contains a working FastAPI backend, a static frontend, and a JSON-backed task store under backend/data/tasks.json.
- Confirmed that the current implementation supports task CRUD, tag normalization/validation, activity logging, and task filtering.
- Baseline validation included running the full test suite before the break-test demonstrations.

## Backend Test Results
- Command run: `pytest -q`
- Result: `24 passed`
- Warnings: 3 warnings from FastAPI/Starlette deprecation notices.

Key verified tests:
- `test_create_task_with_tags_normalizes_and_returns_tags`
- `test_create_task_with_blank_tag_returns_422`
- `test_activity_endpoint_records_create_update_and_delete_events`
- `test_activity_endpoint_records_status_change_events`

## Break Test Evidence

The following break tests were performed by deliberately introducing a temporary defect, running the relevant test, restoring the code, and rerunning the test to confirm the fix.

### 1. Tag validation break test
- Temporary defect introduced: the blank-tag validation inside `backend/app/tags.py` was disabled so blank values were accepted.
- Command run:
  ```powershell
  pytest -q tests/test_tasks.py -k "blank_tag"
  ```
- Observed result:
  ```text
  1 failed, 23 passed
  ```
  The failure showed that the API returned `201` instead of the expected `422` for a request containing a blank tag.
- Restoration: the original validation logic was restored.
- Verification after restoration:
  ```powershell
  pytest -q tests/test_tasks.py -k "blank_tag"
  ```
  Result:
  ```text
  1 passed
  ```

### 2. Activity logging break test
- Temporary defect introduced: the create-event append step in `backend/app/storage.py` was removed so new tasks would no longer create activity entries.
- Command run:
  ```powershell
  pytest -q tests/test_tasks.py -k "activity_endpoint_records_create_update_and_delete_events"
  ```
- Observed result:
  ```text
  1 failed, 23 passed
  ```
  The failure showed that the activity endpoint no longer contained the expected create/update/delete sequence for the test scenario.
- Restoration: the original activity append logic was restored.
- Verification after restoration:
  ```powershell
  pytest -q tests/test_tasks.py -k "activity_endpoint_records_create_update_and_delete_events"
  ```
  Result:
  ```text
  1 passed
  ```

### 3. Status-change activity break test
- Temporary defect introduced: the status-change activity append in `backend/app/storage.py` was disabled so status updates would not record a change event.
- Command run:
  ```powershell
  pytest -q tests/test_tasks.py -k "status_change_events"
  ```
- Observed result:
  ```text
  1 failed, 23 passed
  ```
  The failure showed that the activity endpoint did not include the expected status-change event after a task status update.
- Restoration: the original status-change logging logic was restored.
- Verification after restoration:
  ```powershell
  pytest -q tests/test_tasks.py -k "status_change_events"
  ```
  Result:
  ```text
  1 passed
  ```

## Final Verification
- Command run after all restores:
  ```powershell
  pytest -q
  ```
- Result:
  ```text
  24 passed, 3 warnings
  ```

The current implementation satisfies the documented contract, and the break-test evidence above confirms that the relevant functionality is working and recoverable after deliberate defects.