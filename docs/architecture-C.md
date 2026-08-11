# Task Tracker — Architecture (Strategy C: Targeted Context)

## 1. What the app does
A FastAPI application (title: "Task Tracker API") exposing endpoints to create, read, update,
and delete tasks, and to list recorded activity events, with state persisted to a JSON file. What
the app is *for* beyond that (course project, intended audience, frontend) is not visible from
the files I read.

## 2. Data model
- **TaskResponse** (the stored/returned task shape): `id`, `title`, `description`, `status`
  (enum: `ToDo`/`InProgress`/`Done`), `priority` (enum: `Low`/`Medium`/`High`), `assignee`,
  `tags` (optional list of strings), `created_at`, `updated_at`.
- **TaskCreate**/**TaskUpdate** (request shapes): same fields as above minus `id`/timestamps;
  both forbid unknown fields; `title` is required on create, optional on update but rejected if
  explicitly set to `null`.
- **ActivityEvent**: `id`, `task_id`, `event_type`, `message`, `timestamp`.

## 3. Request flow — creating a task
`POST /tasks` (`main.py`) receives a `TaskCreate` body → pydantic validates it (`models.py`:
`title` is stripped and must be 1–200 chars; `tags`, if present, are normalized by a function
imported from a separate `tags` module) → `storage.add_task` (`storage.py`) generates a UUID,
sets `created_at`/`updated_at` to the current UTC time, stores the task in an in-memory dict,
appends a `"create"` entry to an in-memory activity list, rewrites the *entire* JSON state file,
and returns the task → the route returns it with `201` and `response_model_exclude_none=True`.

## 4. Key files
- `backend/app/main.py` — read directly. Defines every route inline (`/health`, `/tasks`,
  `/tasks/{id}`, `/activity`); configures CORS restricted to `http://localhost:5500`.
- `backend/app/models.py` — read directly. Pydantic request/response models; all forbid unknown
  fields.
- `backend/app/storage.py` — read directly. In-memory dict/list, full-file JSON persistence to a
  `data/tasks.json` path relative to this module.
- `backend/app/business_rules.py` — **not read this pass**; known only to exist because
  `main.py` imports `validate_status_transition` from it and calls it during `PATCH`.
- `backend/app/tags.py` — **not read this pass**; known only to exist because `models.py`
  imports `normalize_tags` (and two constants) from it.
- The persisted data file itself (path constructed in `storage.py` as `<package>/data/tasks.json`) —
  not opened/inspected, only its path and JSON shape (`{"tasks": [...], "activity": [...]}`, with a
  legacy list-shaped fallback) are visible in `storage.py`.

## 5. Conventions
- **Validation**: `title` stripped and length-checked (1–200 chars) directly in `models.py`; tag
  validation is delegated to an external function — the actual count/length limits are not
  visible from the files I read. All request models set `extra="forbid"`.
- **Storage**: single in-memory dict (`_tasks`) and list (`_activity_events`), rewritten in full
  to one JSON file on every mutation; no database; `storage.py` tolerates two different JSON
  shapes on load (a bare list, or a dict with `"tasks"`/`"activity"` keys) with no error handling
  around a malformed file otherwise.
- **Error handling**: `main.py` raises `404` with the message `"Task with id {id} not found"` for
  missing tasks on `GET`/`PATCH`/`DELETE`. Status-transition validation is delegated to
  `business_rules.validate_status_transition` — what it actually enforces is not visible from the
  files I read.
- **Frontend/backend interaction**: CORS in `main.py` allows only origin `http://localhost:5500`.
  Whether a frontend exists, what it looks like, or what URL it calls is not visible from the
  files I read.

## 6. Not visible or assumptions
- Exact tag count/length limits — not visible from the files I read (delegated to `tags.py`).
- Exact status-transition rules — not visible from the files I read (delegated to
  `business_rules.py`).
- Whether a frontend exists and how it behaves — not visible from the files I read.
- Test conventions, CI/Docker setup, dependency list — not visible from the files I read.
- Whether this is a course project, and any documented limitations — not visible from the files
  I read.
