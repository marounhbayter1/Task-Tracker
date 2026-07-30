def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Add API coverage",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Ada",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "id",
        "title",
        "description",
        "status",
        "priority",
        "assignee",
        "created_at",
        "updated_at",
    }
    assert body["title"] == "Write tests"
    assert body["description"] == "Add API coverage"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Ada"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"priority": "Low"})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post(
        "/tasks",
        json={"title": "Invalid priority", "priority": "Urgent"},
    )

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post(
        "/tasks",
        json={"title": "Unknown field", "unexpected": True},
    )

    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "Todo task", "status": "ToDo"})

    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    low = client.post(
        "/tasks",
        json={"title": "Low task", "priority": "Low"},
    ).json()
    client.post("/tasks", json={"title": "High task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "Low"})

    assert response.status_code == 200
    assert response.json() == [low]


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    assert response.json() == created_task


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    missing_id = "missing-task-id"

    response = client.get(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}


def test_patch_partial_update_keeps_other_fields(client):
    task = client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "priority": "High",
            "assignee": "Ada",
        },
    ).json()

    response = client.patch(
        f"/tasks/{task['id']}",
        json={"description": "Updated description"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task["id"]
    assert body["title"] == "Original title"
    assert body["description"] == "Updated description"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Ada"


def test_patch_not_found_returns_404(client):
    missing_id = "missing-task-id"

    response = client.patch(f"/tasks/{missing_id}", json={"title": "Updated"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "Done"},
    )

    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "ToDo"},
    )

    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    missing_id = "missing-task-id"

    response = client.delete(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}
