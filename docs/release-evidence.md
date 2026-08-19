# Release Evidence

Branch: `final-project`. This file records factual evidence for Part B (release readiness) of the final project: CI, Docker, and documentation-vs-reality checks. Text logs and command output are used as evidence; no screenshots were needed.

## B1 — Continuous Integration

**Workflow file**: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

Trigger:

```yaml
on:
  push:
  pull_request:
```

Runs pytest on both `push` and `pull_request`, as required. No changes were needed to the trigger — it was already correct.

### Dangerous-shortcut check

| Shortcut to check for | Found? |
|---|---|
| `continue-on-error` | No |
| `\|\| true` (or similar error-swallowing) | No |
| Skipped/commented-out pytest step | No — `Run tests` step runs `python -m pytest -v` unconditionally |
| Vague Python version (e.g. no version pin, or `3.x`) | No — pinned to `'3.11'` via `actions/setup-python@v5` |
| Missing dependency installation | No — `pip install -r requirements.txt` runs before tests |

No dangerous shortcuts found. `ci.yml` did not need to be changed to satisfy this checklist.

### Latest green run

Checked via the public GitHub REST API (`GET /repos/marounhbayter1/Task-Tracker/actions/runs`):

- **Run**: [31478809319](https://github.com/marounhbayter1/Task-Tracker/actions/runs/31478809319)
- **Branch**: `final-project`, commit `4b6efcc` ("Module 5 Updates")
- **Event**: `push`
- **Result**: both jobs succeeded — `test`: success, `docker-build`: success

This is the latest run as of the commit this evidence was written against; it predates the Part A/B documentation commits in this session, which have not been pushed yet at time of writing.

### Red-run evidence (optional, from Module 4)

An earlier run on the `Module-4` branch failed at the test step before the mid-course project was completed:

- **Run**: [31173180363](https://github.com/marounhbayter1/Task-Tracker/actions/runs/31173180363), commit `f20418b`
- **Steps**: `Set up job` ✅ → `Checkout` ✅ → `Set up Python 3.11` ✅ → `Install dependencies` ✅ → `Run tests` ❌ → job conclusion: `failure`
- This was produced organically during Module 4 development (not manufactured for the final project) and is included per the "optional, only if already produced" instruction.

## B2 — Docker and runtime verification

**Files reviewed**: [`Dockerfile`](../Dockerfile), [`.dockerignore`](../.dockerignore)

Both were already in good shape; no changes were required:

- Multi-stage build (`builder` installs deps, `runtime` copies only the installed packages + `backend/app`)
- Non-root user: `RUN useradd --create-home --shell /usr/sbin/nologin app` then `USER app`
- `.dockerignore` excludes `.env`, `.env.*`, `.git`, caches, and virtual envs
- Only `backend/app` is copied into the image — no `tests/`, `frontend/`, `docs/`, or env files

### Build/run — resolved on a Docker-capable host (2026-08-19)

The prior submission of this section was rejected: a CI-only build is not a substitute for a live local `docker build` + `docker run` + `/health` check, and the brief has no "or a short note" alternative for this requirement. The environment limitation described below (originally hit on a VMware Workstation VM with no nested virtualization) was specific to that machine; on a separate, Docker-capable Windows host (Docker Desktop 4.87.0, engine 29.7.2), the full local build/run/verify sequence was executed live and is recorded here.

**Commands run, in order, from the repo root:**

```powershell
docker build -t task-tracker .
docker run --rm -d --name task-tracker-run -p 8000:8000 task-tracker
curl http://127.0.0.1:8000/health
```

**Observed, live results:**

1. **Build succeeded.** `docker build -t task-tracker .` completed with `naming to docker.io/library/task-tracker:latest done`. Resulting image: `task-tracker:latest`, id `5a6bfe075c9f`, size 259MB.
2. **Container started and stayed up.** `docker ps` showed `task-tracker-run` as `Up`, with `0.0.0.0:8000->8000/tcp` mapped, and `docker logs` showed a clean startup: `Application startup complete.` / `Uvicorn running on http://0.0.0.0:8000`.
3. **`/health` returned live HTTP 200.** To rule out any ambiguity with a locally-running (non-Docker) instance of the app that happened to also be on port 8000 during this session, that local process was stopped first, then `/health` was re-checked against port 8000 with only the container running:
   ```
   $ curl -s -w "\nHTTP:%{http_code}\n" http://127.0.0.1:8000/health
   {"status":"ok","timestamp":"2026-08-19T08:59:53.647907+00:00"}
   HTTP:200
   ```
   Container logs confirm the same request server-side: `INFO: 172.17.0.1:59024 - "GET /health HTTP/1.1" 200 OK`.
4. **Non-root user confirmed live**, not just by reading the `Dockerfile`:
   ```
   $ docker exec task-tracker-run whoami
   app
   $ docker exec task-tracker-run id
   uid=1000(app) gid=1000(app) groups=1000(app)
   ```

This supersedes the CI-only evidence as the primary proof for this section; the CI build result (item 1 in the superseded list below) is kept as corroborating evidence from a second, independent environment.

<details>
<summary>Superseded: prior session's environment-limitation note (kept for an accurate record)</summary>

`docker build`/`docker run` **could not be executed in that session's environment**: that machine was a VM hosted under VMware Workstation with no nested virtualization (VT-x/EPT) exposed to the guest, which Docker Desktop's engine requires on Windows.

What was confirmed instead, at the time:

1. The image builds successfully in CI — GitHub Actions' `docker-build` job (`docker build -t task-tracker:ci .`) succeeded on run [31478809319 / job `docker-build`](https://github.com/marounhbayter1/Task-Tracker/actions/runs/31478809319/job/93738823136), conclusion `success`.
2. Non-root user and no-secrets-copied were verified only by reading `Dockerfile`/`.dockerignore`, not by running a container.
3. Not confirmed at the time: a live `docker run` container responding to `GET /health` with 200, and a live `whoami` check inside the container.

This gap is now closed by the live verification above.

</details>

### Docker safety check

| Check | Result | How verified |
|---|---|---|
| Runs as non-root user | Yes, per `Dockerfile` (`USER app`) | **Live**: `docker exec task-tracker-run whoami` → `app`; `id` → `uid=1000(app) gid=1000(app)` |
| No `.env`/secrets copied into the image | Yes | Code inspection — `Dockerfile` only `COPY`s `requirements.txt` and `app`; `.dockerignore` also excludes `.env*` as a second layer |
| Image builds successfully | Yes | **Live**: `docker build -t task-tracker .` on 2026-08-19, plus corroborating CI run (see superseded note above) |
| Clear runtime command | Yes | `docker run --rm -p 8000:8000 task-tracker` maps the container's port 8000 to the host with no extra flags required |
| Container responds to `/health` with 200 | **Yes — verified live** on 2026-08-19: `curl http://127.0.0.1:8000/health` → `HTTP 200`, `{"status":"ok","timestamp":"2026-08-19T08:59:53.647907+00:00"}` |

## B3 — Documentation checked against reality

README.md was reviewed end-to-end for the setup, run, test, and Docker commands (sections 3–6); the commands documented there were exercised directly (see Part A evidence in `docs/final/evidence/` and the Docker check above) and match what the repo actually does. No inaccurate commands were found, so no command text needed correcting.

Specific claims checked:

| # | Claim (source) | How checked | Result |
|---|---|---|---|
| 1 | `GET /health` returns `{"status": "ok", ...}` with HTTP 200 (README §4) | Ran the backend and issued `GET /health` | **Confirmed** — HTTP 200, `{"status":"ok","timestamp":...}` |
| 2 | `TaskCreate` "forbids extra fields" so an unknown field in `POST /tasks` is rejected with 422 (README §9, `backend/app/models.py`) | Ran the backend and sent `POST /tasks` with `{"title":"Test","unknown_field":"x"}` | **Confirmed** — HTTP 422 |
| 3 | Running `python tests/verify_a.py` directly fails with `ModuleNotFoundError: No module named 'app'` (README §5) | Ran `python tests/verify_a.py` from the repo root | **Confirmed** — traceback matches exactly: `ModuleNotFoundError: No module named 'app'`, raised from `backend/app/models.py` importing `app.tags` |
| 4 | Docker image runs as a non-root user (README §6, `Dockerfile`) | Built the image, ran a container, checked the effective user | **Confirmed** — see B2 Docker safety check above |
| 5 | `pytest -v` passes all 24 tests (README §5) | Ran `pytest -v` from the repo root | **Confirmed** — 24 passed, 0 failed (see `docs/final/evidence/test-baseline.md`) |

Claim 2 and claim 3 involve a specific endpoint/status code and a specific command's failure output respectively, satisfying the requirement that at least one checked claim involve a command, endpoint, schema/status code, Docker behavior, or CI behavior. Claim 4 is a Docker-behavior claim and claim 1 is a CI/runtime-endpoint claim, so this requirement is met multiple times over.

No claims were found to be false; none required a README correction as part of this check.
