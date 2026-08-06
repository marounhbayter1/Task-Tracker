# Task Tracker

Task Tracker is a small full-stack task management app built with FastAPI and a static frontend. The backend stores tasks and activity history in a local JSON file, supports task CRUD, normalizes and validates tags, and records create, update, delete, and status-change activity events.

## Features

- Create, read, update, and delete tasks
- Filter tasks by status and priority
- Normalize and validate tags by trimming whitespace, rejecting blank tags, and enforcing a maximum tag count
- Record activity events for task creation, updates, deletion, and status changes
- Use a simple frontend for creating tasks and viewing recent activity

## Project structure

```text
task-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── business_rules.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── storage.py
│   │   └── tags.py
│   └── data/
│       └── tasks.json
├── docs/
│   └── midcourse/
├── frontend/
│   └── index.html
├── tests/
├── requirements.txt
└── README.md
```

## Setup

From the project root, create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

If you want a local environment file, copy the example file:

```powershell
Copy-Item .env.example .env
```

## Run the backend

Start the API from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

The health endpoint is available at http://127.0.0.1:8000/health.

## Run the frontend

Open the static frontend directly in a browser:

- Open frontend/index.html directly, or
- Serve the frontend directory with a simple local web server:

```powershell
python -m http.server 5500 --directory frontend
```

Then browse to http://127.0.0.1:5500.

## Run tests

From the project root, run:

```powershell
pytest -q
```

## API documentation

With the backend running, open Swagger UI at http://127.0.0.1:8000/docs.

## Documentation

Project notes, design decisions, user stories, and verification evidence are stored in the docs/midcourse folder.
