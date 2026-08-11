# Task Tracker — Architecture (Strategy B: Structured Context)

## 1. What the app does
Task Tracker is a Module 4/5 course project: a small full-stack task-management app with a
FastAPI backend exposing task and activity endpoints, backed by a local JSON file instead of a
database, and a single static HTML/JS page as the frontend. It does not implement authentication,
a database, or production deployment.

## 2. Data model
Named fields/entities (per AGENTS.md's business rules and the file summaries):
- **Task**: `title` (required, trimmed, 1–200 chars), `description` (referenced only via a
  PATCH-null quirk), `status` (enum: `ToDo`/`InProgress`/`Done`), `priority` (enum: `Low`/
  `Medium`/`High`), `tags` (list, ≤10 tags, ≤30 chars each). Request bodies (`TaskCreate`/
  `TaskUpdate`) forbid unknown fields.
- **Activity event**: recorded event types are `create`, `update`, `status_change`, `delete`,
  persisted alongside tasks in `backend/data/tasks.json`. No other field names for this entity are
  given in the available context.

## 3. Request flow — creating a task
A request hits a route defined inline in `backend/app/main.py` (no separate router files) → the
body is validated by a pydantic model in `backend/app/models.py` (`extra="forbid"`; `title`
trimmed/length-checked; `tags` normalized against the tag rules) → the validated data is handed to
`backend/app/storage.py`, which holds an in-memory dict/list and rewrites the *entire* JSON file on
every mutation (no database) → a `create` activity event is recorded, per the business-rules
summary. The exact response status code and function/variable names are not stated in this
context (see section 6).

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
- **Validation**: `title` trimmed to 1–200 chars; `tags` capped at 10 items of ≤30 chars; request
  models reject unknown fields (`422`).
- **Storage**: single-process, in-memory source of truth, rewritten to one JSON file on every
  mutation; no database; no pagination mentioned for list endpoints.
- **Error handling**: invalid status transitions and validation failures return `422`. Behavior
  for not-found resources is not stated in this context (see section 6).
- **Frontend/backend interaction**: frontend is a static Kanban board + activity feed; CORS is
  locked to `http://localhost:5500`. The frontend's own API base URL is not stated in this context.

## 6. Not visible or assumptions
- No field named `id`, `assignee`, `created_at`, or `updated_at` appears anywhere in AGENTS.md or
  the file summaries — this context cannot confirm the full `Task` shape.
- The `ActivityEvent` entity's own fields (beyond its event-type values) are not named.
- HTTP status codes for success/not-found responses (e.g. `201`, `404`) are not stated.
- The frontend's hardcoded API base URL is not given in this context.
- `requirements.txt` lists `httpx2`, not `httpx` — AGENTS.md flags this as unusual and unconfirmed.
- Whether this repo is public or private is not addressed by either source.
