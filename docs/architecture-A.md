# Task Tracker — Architecture (Strategy A: Minimal Context)

## 1. What the app does
Task Tracker is a small course project: a FastAPI backend exposes CRUD endpoints for tasks and a
read-only activity log, backed by a local JSON file instead of a database, with a single static
HTML/JS page as the frontend.

## 2. Data model
- **Task** (`TaskResponse`): `id` (UUID), `title` (1–200 chars), `description` (str, unbounded),
  `status` (enum: `ToDo`/`InProgress`/`Done`), `priority` (enum: `Low`/`Medium`/`High`),
  `assignee` (optional str, unbounded), `tags` (list[str], ≤10 tags, ≤30 chars each),
  `created_at`/`updated_at` (UTC datetime).
- **ActivityEvent**: `id`, `task_id`, `event_type` (`create`/`update`/`status_change`/`delete`),
  `message`, `timestamp`.
- Both collections persist together in `backend/data/tasks.json` as `{"tasks": [...], "activity": [...]}`.

## 3. Request flow — creating a task
`POST /tasks` → FastAPI validates the body against `TaskCreate` (strips/checks `title` length,
normalizes `tags`, rejects unknown fields) → `create_task` calls `storage.add_task` → a UUID and
timestamps are generated, the task is stored in the in-memory `_tasks` dict, a `create`
`ActivityEvent` is appended, and the *entire* store is rewritten to `tasks.json` → the created
`TaskResponse` is returned with `201`.

## 4. Key files
- `backend/app/main.py` — all routes (`/health`, `/tasks*`, `/activity`) defined inline, no router files.
- `backend/app/models.py` — pydantic request/response models; `extra="forbid"` on all of them.
- `backend/app/storage.py` — in-memory dict/list + full-file JSON persistence, no database.
- `backend/app/business_rules.py` — fixed status-transition rules (`ToDo→InProgress→Done→InProgress`).
- `backend/app/tags.py` — tag normalization/limits (≤10 tags, ≤30 chars).
- `frontend/index.html` — single static page: Kanban board + activity panel, plain JS, no build step.
- `tests/test_tasks.py` / `tests/conftest.py` — pytest API tests via `TestClient`, storage reset per test.
- `backend/data/tasks.json` — the persisted data file itself.

## 5. Conventions
- **Validation**: pydantic `field_validator`s strip/length-check strings; all request models set
  `extra="forbid"` (unknown fields → `422`).
- **Storage**: single-process, in-memory source of truth, rewritten to one JSON file on every
  mutation; no locking, no database, no pagination on list endpoints.
- **Error handling**: `HTTPException` with plain-text `detail` (404 not-found, 422 validation/
  business-rule violations); no global exception handler, no stack traces leaked.
- **Frontend/backend interaction**: frontend calls a hardcoded `http://localhost:8000` via `fetch`;
  CORS locked to `http://localhost:5500`; no auth on either side.

## 6. Not visible or assumptions
- Whether this repo is public or private is not visible from the files.
- Concurrent-write behavior on `tasks.json` (two processes writing at once) is not confirmed.
- Docker volume/persistence behavior for `backend/data/` across container restarts is not confirmed
  (flagged as `[VERIFY]` in the repo's own decision notes).
- `requirements.txt` lists `httpx2`, not `httpx` — unconfirmed whether this is intentional.
