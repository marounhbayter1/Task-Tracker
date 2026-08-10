# Technical Decision Note: In-Memory Task Storage

**Status:** Draft
**Module:** 4 — Task Tracker

## 1. Context

The Task Tracker backend (`backend/app/main.py`, FastAPI) needs to persist tasks and activity
events (create/update/delete/status-change) across requests within a single running process, and
needs that data to survive a process restart without standing up a database.

The current implementation (`backend/app/storage.py`) keeps two module-level Python objects —
a `dict[str, TaskResponse]` (`_tasks`) and a `list[ActivityEvent]` (`_activity_events`) — as the
live source of truth. Every mutation (`add_task`, `update_task`, `delete_task`) writes through to
`backend/data/tasks.json` by re-serializing the *entire* in-memory state and rewriting the file
(`_save_state`). On process start, `_load_state` reads that file back into the two in-memory
structures. Reads (`get_all_tasks`, `get_task_by_id`, `get_activity_events`) only ever touch the
in-memory dict/list, never the file.

There is no database, no ORM, and no external storage service in this project.

## 2. Decision

Task and activity data is held in in-memory Python data structures (a dict keyed by task id, and
a list of activity events) for the lifetime of the process, and that state is persisted to a
single local JSON file on every write so it survives a restart. All reads are served from memory,
never from disk. There is no database, no locking, and no support for multiple processes or
instances sharing state — this app is single-process by design.

## 3. Alternatives Considered

- **Database (e.g. SQLite/Postgres) as the source of truth.** Rejected for this module's scope —
  no database is set up anywhere in this project (Dockerfile, CI, and README all confirm this),
  and the course project explicitly does not claim database-backed storage.
- **In-memory only, no file persistence.** Would lose all tasks on every process restart
  (including `--reload` during local development, and every container restart). Rejected because
  the JSON file gives restart-survival at low implementation cost.
- **File-backed reads (read from disk on every request).** Rejected in favor of reading from the
  in-memory dict/list, which is simpler and avoids repeated disk I/O per request; the file is
  written on mutation but not read again until process start.

## 4. Trade-offs

DRAFT - REWRITE IN MY OWN WORDS

- Every single mutation rewrites the *entire* `tasks.json` file (`_save_state` dumps all tasks and
  all activity events, not a diff). This is simple but means write cost grows with total data
  size, and there's no partial-write or append path.
- There is no file locking around reads/writes (`backend/app/storage.py`). [VERIFY] The README
  states this is "not designed for concurrent multi-process/multi-instance use" — I have not
  independently verified what happens under concurrent writes (e.g. two `uvicorn --reload`
  processes, or multiple container replicas), only that no locking code exists to prevent
  corruption.
- The Docker image (`Dockerfile`) copies in `backend/app` only and does not declare a volume for
  `backend/data/`, and there's no `docker-compose` in this repo. [VERIFY] I have not confirmed
  whether `backend/data/tasks.json` persists across `docker run` invocations or is lost when the
  container is removed — this depends on default container filesystem behavior that I have not
  tested here.
- CI (`.github/workflows/ci.yml`) runs `pytest` and then `docker build`, but does not run the
  container or exercise the persistence path at all — so the file-persistence behavior is
  untested in CI.
- I would do this differently by...

## 5. Consequences

- The app can be restarted (locally or via `--reload`) without losing previously created tasks or
  activity history, because state is reloaded from `backend/data/tasks.json` on startup.
- The app cannot be horizontally scaled (multiple processes/instances) without risking data
  corruption or lost writes, since there is no locking or coordination between processes sharing
  the same file.
- Read performance is fast and simple (pure in-memory dict/list access), at the cost of write
  performance scaling poorly as the number of tasks/activity events grows, since every write
  rewrites the full file.
- Adding real concurrency, multi-instance deployment, or durability guarantees beyond "single
  local file" would require replacing this storage layer with a database — this design does not
  evolve incrementally into one.

## 6. Open Questions

DRAFT - REWRITE IN MY OWN WORDS

- [VERIFY] What actually happens to `backend/data/tasks.json` when the Docker container is
  stopped and removed vs. restarted — is it lost, and should a volume be documented/added?
- [VERIFY] What happens if two processes (e.g. a local `--reload` dev server plus a second
  process) write to `tasks.json` concurrently — is corruption possible, or does the last write
  simply win silently?
- At what data size (task count, activity event count) does the full-file rewrite on every
  mutation become a noticeable latency problem, and would that be the trigger for moving to a
  database?
- Is a database migration in scope for a future module, or is single-process JSON-file storage
  the accepted end state for this project?
