# Frontend baseline check

Date: 2026-08-11
Branch: `final-project`

## How the frontend was opened

Served the static frontend from the repo root, matching the README's documented command:

```powershell
python -m http.server 5500 --directory frontend
```

Then opened `http://localhost:5500` in the default browser (using `localhost`, not `127.0.0.1`, because the backend's CORS config in `backend/app/main.py` only allows the `http://localhost:5500` origin — this matches the README's note in section 4). The backend from the [backend health check](backend-health-check.md) was running at the same time on port 8000 so the page could call `/tasks` and `/activity`.

## Confirmation

The Kanban board (To Do / In Progress / Done columns) rendered with the sample tasks, and clicking "New Task" / a task's "Edit" button opened the create/edit modal form (title, description, status, priority, assignee, tags) — the create-edit flow is still visible and functional, matching the mid-course behavior with no code changes.
