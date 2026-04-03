# 1. Submit tasks, get back scheduled + buffered
async def test_schedule_tasks(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "task a", "resources": ["camera", "disk"], "profit": 9.2},
                {"name": "task b", "resources": ["disk"], "profit": 0.4},
                {"name": "task c", "resources": ["proc"], "profit": 2.9},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_profit"] == 12.1  # task a + task c
    assert len(data["scheduled"]) == 2
    assert len(data["buffered"]) == 1
    assert data["buffered"][0]["name"] == "task b"


# 2. Buffered tasks persist and get re-evaluated with new submissions
async def test_buffer_reevaluated_with_new_tasks(client):
    # First batch: one task with "disk"
    await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "heavy disk", "resources": ["disk"], "profit": 1.0},
            ]
        },
    )
    # Second batch: task with "disk" + higher profit → should displace
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "big disk", "resources": ["disk"], "profit": 10.0},
            ]
        },
    )
    data = resp.json()
    assert any(t["name"] == "big disk" for t in data["scheduled"])
    assert any(t["name"] == "heavy disk" for t in data["buffered"])


# 3. List tasks filtered by status
async def test_list_scheduled_tasks(client):
    await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "a", "resources": ["x"], "profit": 1.0},
                {"name": "b", "resources": ["y"], "profit": 2.0},
            ]
        },
    )
    resp = await client.get("/tasks/?status=scheduled")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# 4. Delete a task
async def test_delete_task(client):
    create = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "delete me", "resources": [], "profit": 1.0},
            ]
        },
    )
    task_id = create.json()["scheduled"][0]["id"]
    resp = await client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204


# 5. Validation: empty name → 422
async def test_validation_empty_name(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "", "resources": [], "profit": 1.0},
            ]
        },
    )
    assert resp.status_code == 422


# 6. Validation: negative profit → 422
async def test_validation_negative_profit(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "bad", "resources": [], "profit": -1.0},
            ]
        },
    )
    assert resp.status_code == 422


# 7. Scheduler picks optimal for small input (exact solver)
async def test_optimal_scheduling(client):
    # Greedy would pick profit 6, but two non-conflicting tasks sum to 10
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "big", "resources": ["a", "b"], "profit": 6.0},
                {"name": "x", "resources": ["a"], "profit": 5.0},
                {"name": "y", "resources": ["b"], "profit": 5.0},
            ]
        },
    )
    data = resp.json()
    assert data["total_profit"] == 10.0
