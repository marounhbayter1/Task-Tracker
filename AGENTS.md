# AGENTS.md

Guidance for AI agents (and humans acting like one) working in this repository.

## 1. Project summary

Task Tracker is a Module 4/5 course project: a small full-stack task-management app.

- **Backend**: FastAPI app in `backend/app/` exposing task and activity endpoints.
- **Storage**: a local JSON file (`backend/data/tasks.json`), loaded into an in-memory dict and rewritten on every mutation (`backend/app/storage.py`). No database.
- **Frontend**: a single static page, `frontend/index.html` (no build step) — a drag-and-drop Kanban board plus an activity feed.
- **Tests**: pytest suite in `tests/`, exercising the API via FastAPI's `TestClient`.
- **CI**: GitHub Actions (`.github/workflows/ci.yml`) runs the test suite, then builds the Docker image.

It does not implement authentication, a database, or production deployment. See README.md section 9 for the full list of current limitations.

## 2. Tech stack and commands

Confirmed by reading `requirements.txt`, `README.md`, `Dockerfile`, and `.github/workflows/ci.yml`.

- **Language/runtime**: Python 3.11 (pinned in CI and Docker). README notes it has also been run locally on 3.12 — not confirmed as officially supported.
- **Dependencies** (`requirements.txt`): `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `pytest`, `httpx2`. Note: the last entry is literally `httpx2`, not `httpx` — this is unusual (FastAPI's `TestClient` normally depends on `httpx`). Not confirmed whether this is intentional; do not silently "fix" it.

**Run the backend** (from repo root):
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```
or, without changing directories:
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
API at `http://127.0.0.1:8000`, health check at `/health`, Swagger UI at `/docs`.

**Run the frontend** (static, no build step):
```powershell
python -m http.server 5500 --directory frontend
```
Then browse to `http://127.0.0.1:5500`. CORS in `backend/app/main.py` only allows origin `http://localhost:5500` (not `127.0.0.1:5500`).

**Run tests** (from repo root, venv active):
```powershell
pytest -v
```
`tests/conftest.py` adds `backend/` to `sys.path`. README states 24 tests currently pass.

- `tests/verify_a.py` is **not** a supported entry point — running it directly raises `ModuleNotFoundError` per README section 5. Treat it as reference code only.

**Docker**:
```powershell
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```
README flags this as **[VERIFY]** — transcribed from `Dockerfile`/CI but not executed against a live Docker daemon.

## 3. Business rules visible in the code

- **Task status** (`backend/app/models.py`, `TaskStatus`): `ToDo`, `InProgress`, `Done`.
- **Task priority** (`TaskPriority`): `Low`, `Medium`, `High`.
- **Status transitions** (`backend/app/business_rules.py`): only
  `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress` are valid.
  Any other transition — including setting a status to its current value — returns `422`.
- **Title** (`models.py`): required, trimmed, 1–200 characters; blank after trim is rejected.
- **Tags** (`backend/app/tags.py`): at most 10 tags, each ≤30 characters, non-blank after trimming; must be a list of strings.
- **Strict request bodies**: `TaskCreate`/`TaskUpdate` use `extra="forbid"` — unknown fields return `422`.
- **Partial-update (`PATCH`) quirks** (`backend/app/storage.py`):
  - `"description": null` resets description to `""`.
  - `"tags": null` leaves existing tags **unchanged** (does not clear them).
  - `"title": null` is rejected with `422` (not treated as "no change").
  - A `PATCH` with no fields set returns the task unchanged and records no activity event.
- **Activity events** (`storage.py`): `create`, `update`, `status_change`, `delete` — recorded on every mutation and persisted alongside tasks in `backend/data/tasks.json`.
- **No pagination**: `GET /tasks` and `GET /activity` always return the full list.
- **No authentication/authorization**: all endpoints are open.
- **CORS**: locked to `http://localhost:5500` only.
- **Concurrency**: single JSON-file store with no locking — not designed for concurrent multi-process use.

## 4. Module 5 guardrails

These apply to any agent (AI or scripted) operating in this repository under Module 5:

- **Docs-first**: before proposing or making a change, check `README.md` and `docs/` (`docs/decisions/`, `docs/midcourse/`) for existing decisions, rationale, and open questions. Don't re-derive a decision that's already documented — cite it.
- **Read-only by default**: unless a task explicitly asks for a code change, operate in read-only/analysis mode — explore, explain, and propose, but don't edit application files.
- **One task per thread**: scope each conversation/session to a single, clearly-stated task. Don't bundle unrelated changes or expand scope mid-thread.
- **No `backend/app/` changes without explicit approval**: `backend/app/main.py`, `models.py`, `storage.py`, `business_rules.py`, and `tags.py` implement the graded business logic for this module. Do not modify any file under `backend/app/` (or `frontend/index.html`, `requirements.txt`, `Dockerfile`) unless the user has explicitly approved that specific change in the current thread. Documentation files (`README.md`, `docs/**`, `AGENTS.md`) are outside this restriction unless the user says otherwise.

## 5. Security and governance reminders

- **Never paste, print, or otherwise expose secrets.** `.env` exists in this repo — do not read its contents into a response, log, or commit, even to "confirm" a value. `.env.example` is a template and safe to reference.
- **No destructive commands** — no deleting/overwriting `backend/data/tasks.json`, force-pushing, `git reset --hard`, `rm -rf`, or similar, without explicit user confirmation for that specific action.
- **Cite files, don't paraphrase from memory.** Reference the exact file and, where useful, line numbers (e.g. `backend/app/business_rules.py:6-10`) instead of restating rules generically.
- **Do not invent findings.** If a behavior, command, or rule isn't directly visible in the code or docs, mark it **"not confirmed"** rather than asserting it. Several items in this file already follow that convention (see the `httpx2` and Docker notes above).
