# Test baseline check

Date: 2026-08-11
Branch: `final-project`

## Command

```powershell
pytest -v
```

(Run from the repo root with the venv active; `tests/conftest.py` puts `backend/` on `sys.path`, matching README section 5.)

## Result

**24 passed, 0 failed, 3 warnings, in 0.29s.** Full output: [`pytest-output.log`](pytest-output.log).

No failing tests. No test names to record as pre-existing or introduced failures — the suite is green on `final-project` exactly as it was at the end of the mid-course project. No test code or application code was changed to get this result.

The 3 warnings are pre-existing deprecation notices (`httpx`/`starlette.testclient`, and `HTTP_422_UNPROCESSABLE_ENTITY` naming in `backend/app/main.py`) — not failures, and out of scope for Part A, which is a protect-what-exists check, not a refactor.
