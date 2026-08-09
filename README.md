# Task Tracker

Module 4 course project: a small full-stack task management app built with FastAPI and a static HTML/JS frontend. The backend stores tasks and activity history in a local JSON file (`backend/data/tasks.json`), supports task CRUD, normalizes and validates tags, enforces a fixed status-transition workflow, and records create/update/delete/status-change activity events.

## 1. Project overview

- **Backend**: FastAPI app (`backend/app/`) exposing task and activity endpoints, backed by a JSON file instead of a database.
- **Frontend**: a single static page (`frontend/index.html`) for creating tasks and viewing recent activity.
- **Tests**: pytest suite (`tests/`) covering the API via FastAPI's `TestClient`.
- **CI**: GitHub Actions workflow that runs the test suite and then builds the Docker image (see [section 7](#7-ci-workflow-summary)).

Core features:

- Create, read, update, and delete tasks
- Filter tasks by status and priority (`GET /tasks?status=...&priority=...`)
- Normalize and validate tags: trims whitespace, rejects blank tags, and enforces a maximum tag count and length
- Enforce a fixed set of allowed status transitions (see [section 9](#9-project-conventions-and-current-limitations))
- Record activity events for task creation, updates, deletion, and status changes, available via `GET /activity`

This is a course project. It does not implement authentication, a database, or production deployment — see [section 9](#9-project-conventions-and-current-limitations) for the full list of current limitations.

## 2. Prerequisites

- **Python 3.11** — CI (`.github/workflows/ci.yml`) and the Docker image (`Dockerfile`) both pin `3.11`. [VERIFY] Locally this repo has also been exercised with Python 3.12; if you use a different minor version than 3.11, confirm the test suite still passes for you.
- **pip** (bundled with Python)
- **Docker Desktop or Docker Engine** — only needed for [section 6](#6-run-with-docker)
- **A web browser** — only needed to use the static frontend in [section 4](#4-run-the-app-locally)
- Commands below are written for **PowerShell on Windows**, matching this repo's environment. [VERIFY] If your team also develops on macOS/Linux or bash, you'll want POSIX equivalents (e.g. `source venv/bin/activate` instead of `.\venv\Scripts\Activate.ps1`).

## 3. Local setup

Run these from the repository root.

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Optional — copy the example environment file:

```powershell
Copy-Item .env.example .env
```

`.env.example` currently defines `PORT` and `APP_ENV`. `backend/app/main.py` calls `load_dotenv()`, but no code in `backend/app/` currently reads `PORT` or `APP_ENV` (or any other environment variable) — copying `.env` is optional today and does not change app behavior.

## 4. Run the app locally

### Backend

The course command is `uvicorn app.main:app --reload --port 8000`. In this repo, the `app` package lives under `backend/`, so that exact command only resolves from inside the `backend` directory. Run it as:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Equivalent, without changing directories (this is what the previous version of this README documented, and it still works):

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Either way, the API is served at http://127.0.0.1:8000, and the health check is at http://127.0.0.1:8000/health.

With the backend running, interactive API docs (Swagger UI) are available at http://127.0.0.1:8000/docs.

### Frontend

The frontend is a single static file with no build step.

- Open `frontend/index.html` directly in a browser, or
- Serve it with a simple local web server from the repo root:

```powershell
python -m http.server 5500 --directory frontend
```

Then browse to http://127.0.0.1:5500. The backend's CORS configuration (`backend/app/main.py`) only allows requests from `http://localhost:5500`, so use that origin (not `127.0.0.1:5500`) if the frontend needs to call the API from a browser.

## 5. Run tests

From the repository root, with the virtual environment active:

```powershell
pytest -v
```

`tests/conftest.py` adds `backend/` to `sys.path`, so this command works from the repo root without extra configuration. 24 tests currently pass.

There is also a standalone script, `tests/verify_a.py`, that exercises pydantic model validation directly (outside of pytest). As currently written, running it directly (`python tests/verify_a.py`) fails with `ModuleNotFoundError: No module named 'app'`, because it imports `backend.app.models`, which in turn does `from app.tags import ...` — an import path that only resolves when `backend/` (not the repo root) is on `sys.path`. Treat this script as reference/demonstration code rather than a supported entry point until that import path is fixed.

## 6. Run with Docker

The `Dockerfile` builds a multi-stage image that installs dependencies from `requirements.txt`, then copies in only `backend/app` (no tests, frontend, docs, or env files) and runs it as a non-root user.

Build the image from the repo root:

```powershell
docker build -t task-tracker .
```

Run it, mapping the container's port 8000 to your host:

```powershell
docker run --rm -p 8000:8000 task-tracker
```

The API is then available at http://127.0.0.1:8000 (e.g. http://127.0.0.1:8000/health). [VERIFY] These two commands were transcribed directly from `Dockerfile` and `.github/workflows/ci.yml` (which runs `docker build -t task-tracker:ci .`), but could not be executed against a live Docker daemon in this environment to confirm end-to-end — please verify `build`/`run` locally before relying on this section.

Note: the frontend and `tests/` directory are intentionally not copied into the image, and there is no `docker-compose` setup in this repo.

## 7. CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request`, with two jobs:

1. **`test`** (`ubuntu-latest`):
   - Checks out the repository
   - Sets up Python 3.11
   - Installs dependencies with `pip install -r requirements.txt`
   - Runs `python -m pytest -v`
2. **`docker-build`** (`ubuntu-latest`, runs only if `test` succeeds via `needs: test`):
   - Checks out the repository
   - Builds the image with `docker build -t task-tracker:ci .`

The workflow verifies the test suite passes and the Docker image builds; it does not push the image anywhere or deploy it.

## 8. Project structure

```text
Task Tracker/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── business_rules.py   # status-transition rules
│   │   ├── main.py             # FastAPI app and route handlers
│   │   ├── models.py           # pydantic request/response models
│   │   ├── storage.py          # JSON-file-backed task/activity store
│   │   └── tags.py             # tag normalization/validation
│   └── data/
│       └── tasks.json          # persisted tasks + activity events
├── docs/
│   └── midcourse/
│       ├── mini-adr.md         # architecture decision notes
│       ├── prompt-log.md
│       ├── reflection.md
│       ├── user-stories.md
│       └── verification.md
├── frontend/
│   └── index.html              # static frontend, no build step
├── tests/
│   ├── conftest.py             # TestClient fixture, sys.path setup
│   ├── test_tasks.py           # pytest API tests
│   └── verify_a.py             # standalone model-validation script (see section 5)
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## 9. Project conventions and current limitations

- **Storage**: tasks and activity events are stored in a single JSON file (`backend/data/tasks.json`) via an in-memory dict that is rewritten to disk on every mutation (`backend/app/storage.py`). There is no database.
- **No authentication or authorization**: all endpoints are open; there is no user model or session/token handling.
- **CORS is locked down**: `backend/app/main.py` only allows the origin `http://localhost:5500`.
- **Strict request models**: `TaskCreate`/`TaskUpdate` use `model_config = ConfigDict(extra="forbid")`, so unknown fields in a request body are rejected with `422`.
- **Fixed status workflow**: `backend/app/business_rules.py` only allows `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`. Any other transition — including setting a status to its current value — returns `422`.
- **Tag limits**: at most 10 tags per task, each at most 30 characters, non-blank after trimming (`backend/app/tags.py`).
- **Title limits**: 1–200 characters after trimming; blank titles are rejected.
- **Partial-update quirks** (`backend/app/storage.py`): sending `"description": null` in a `PATCH` resets the description to `""`; sending `"tags": null` leaves the existing tags unchanged (it does not clear them); sending `"title": null` is rejected with `422` rather than treated as "no change."
- **No pagination**: `GET /tasks` and `GET /activity` always return the full list.
- **Single-process only**: the JSON-file store has no locking, so it is not designed for concurrent multi-process/multi-instance use.
- This is a learning project. It does **not** claim deployment readiness, production hardening, authentication, or database-backed storage.

## 10. Documentation and decisions

Design decisions, user stories, and verification evidence for this module are in `docs/midcourse/`:

- [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) — architecture decision notes covering the activity/event-tracking feature and the tags feature (options considered and why the current approach was chosen)
- [`docs/midcourse/user-stories.md`](docs/midcourse/user-stories.md)
- [`docs/midcourse/verification.md`](docs/midcourse/verification.md)
- [`docs/midcourse/reflection.md`](docs/midcourse/reflection.md)
- [`docs/midcourse/prompt-log.md`](docs/midcourse/prompt-log.md)
