# Backend baseline check

Date: 2026-08-11
Branch: `final-project`
Python: 3.12.4 (venv), FastAPI app under `backend/app`

## Command used to start the API

```powershell
cd backend
..\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

(Equivalent to the README's documented `uvicorn app.main:app --reload --port 8000`; `--reload` was omitted only because the process was started non-interactively in the background for this check.)

## Result of `GET /health`

Request:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
```

Response body:

```json
{"status":"ok","timestamp":"2026-08-11T10:36:29.195188+00:00"}
```

HTTP 200. No errors in server output. Full server log for this session: [`backend-server.log`](backend-server.log).

**Conclusion**: the backend starts cleanly from the repo instructions and `/health` responds as documented in the README. No code changes were made to the backend as part of this check.
