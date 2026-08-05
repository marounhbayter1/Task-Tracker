# Task Tracker API

A minimal Module 1 learning project scaffold for a Task Tracker REST API.
The backend uses Python, FastAPI, Pydantic, and local JSON-file storage planned
under `backend/data/`. This skeleton includes the application bootstrap and a
health endpoint; task CRUD and JSON storage are intentionally not implemented yet.

## Project structure

```text
task-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── data/
│       └── tasks.json
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The separate web frontend is intentionally not included in this backend-only
scaffold.

## Setup

From the project root, create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies and copy the example environment file:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run

Start the backend API from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Then open the frontend in your browser by loading the static file:

- Open `frontend/index.html` directly in the browser, or
- Serve the `frontend` directory with a simple local HTTP server such as:

```powershell
python -m http.server 5500 --directory frontend
```

and browse to `http://127.0.0.1:5500`.

## Run tests

From the project root, run:

```powershell
pytest -q
```

## Test the health endpoint

In a second terminal:

```powershell
curl http://127.0.0.1:8000/health
```

The response has this form:

```json
{
  "status": "ok",
  "timestamp": "2026-07-22T12:00:00+00:00"
}
```

## API documentation

With the application running, open [Swagger UI](http://127.0.0.1:8000/docs).
