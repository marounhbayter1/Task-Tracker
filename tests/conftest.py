import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage():
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def created_task(client):
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()
