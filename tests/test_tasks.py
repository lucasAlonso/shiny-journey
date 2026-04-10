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


async def test_empty_task_list(client):
    resp = await client.post("/tasks/", json={"tasks": []})
    assert resp.status_code == 200
    data = resp.json()
    assert data["scheduled"] == []
    assert data["buffered"] == []
    assert data["total_profit"] == 0.0


async def test_single_task(client):
    resp = await client.post(
        "/tasks/",
        json={"tasks": [{"name": "only one", "resources": ["disk"], "profit": 7.5}]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert data["scheduled"][0]["name"] == "only one"
    assert len(data["buffered"]) == 0
    assert data["total_profit"] == 7.5


async def test_all_tasks_conflict(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "low", "resources": ["disk"], "profit": 1.0},
                {"name": "mid", "resources": ["disk"], "profit": 5.0},
                {"name": "high", "resources": ["disk"], "profit": 10.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert data["scheduled"][0]["name"] == "high"
    assert len(data["buffered"]) == 2
    assert data["total_profit"] == 10.0


async def test_all_tasks_compatible(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "t1", "resources": ["a"], "profit": 1.0},
                {"name": "t2", "resources": ["b"], "profit": 2.0},
                {"name": "t3", "resources": ["c"], "profit": 3.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 3
    assert len(data["buffered"]) == 0
    assert data["total_profit"] == 6.0


async def test_task_with_empty_resources(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "no resources", "resources": [], "profit": 4.0},
                {"name": "has resources", "resources": ["disk"], "profit": 3.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 2
    assert data["total_profit"] == 7.0


async def test_three_way_conflict(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "a", "resources": ["disk"], "profit": 2.0},
                {"name": "b", "resources": ["disk"], "profit": 8.0},
                {"name": "c", "resources": ["disk"], "profit": 4.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert data["scheduled"][0]["name"] == "b"
    assert data["total_profit"] == 8.0


async def test_multiple_resources_conflict(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "uses ab", "resources": ["a", "b"], "profit": 3.0},
                {"name": "uses bc", "resources": ["b", "c"], "profit": 3.0},
                {"name": "uses cd", "resources": ["c", "d"], "profit": 3.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_profit"] == 6.0
    scheduled_names = {t["name"] for t in data["scheduled"]}
    assert "uses ab" in scheduled_names
    assert "uses cd" in scheduled_names


async def test_single_resource_blocks_many(client):
    tasks = [{"name": f"low_{i}", "resources": ["x"], "profit": 1.0} for i in range(10)]
    tasks.append({"name": "high", "resources": ["x"], "profit": 50.0})
    resp = await client.post("/tasks/", json={"tasks": tasks})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert data["scheduled"][0]["name"] == "high"
    assert len(data["buffered"]) == 10
    assert data["total_profit"] == 50.0


async def test_buffered_task_gets_scheduled_next_batch(client):
    await client.post(
        "/tasks/",
        json={"tasks": [{"name": "disk task", "resources": ["disk"], "profit": 3.0}]},
    )
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [{"name": "camera task", "resources": ["camera"], "profit": 5.0}]
        },
    )
    data = resp.json()
    scheduled_names = {t["name"] for t in data["scheduled"]}
    assert "disk task" in scheduled_names
    assert "camera task" in scheduled_names
    assert data["total_profit"] == 8.0


async def test_delete_nonexistent_task(client):
    resp = await client.delete("/tasks/9999")
    assert resp.status_code == 404


async def test_list_without_status_filter(client):
    await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "s1", "resources": ["a"], "profit": 1.0},
                {"name": "b1", "resources": ["a"], "profit": 0.5},
            ]
        },
    )
    resp = await client.get("/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_profit_zero_is_valid(client):
    resp = await client.post(
        "/tasks/",
        json={"tasks": [{"name": "zero profit", "resources": [], "profit": 0.0}]},
    )
    assert resp.status_code == 200
    assert len(resp.json()["scheduled"]) == 1


async def test_whitespace_name_rejected(client):
    resp = await client.post(
        "/tasks/",
        json={"tasks": [{"name": "   ", "resources": [], "profit": 1.0}]},
    )
    assert resp.status_code == 422


async def test_multiple_batches_accumulate(client):
    await client.post(
        "/tasks/",
        json={"tasks": [{"name": "batch1_disk", "resources": ["disk"], "profit": 2.0}]},
    )
    await client.post(
        "/tasks/",
        json={"tasks": [{"name": "batch2_disk", "resources": ["disk"], "profit": 3.0}]},
    )
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [{"name": "batch3_cam", "resources": ["camera"], "profit": 4.0}]
        },
    )
    data = resp.json()
    scheduled_names = {t["name"] for t in data["scheduled"]}
    assert "batch2_disk" in scheduled_names
    assert "batch3_cam" in scheduled_names
    assert "batch1_disk" not in scheduled_names


async def test_large_batch_greedy(client):
    tasks = []
    for i in range(50):
        tasks.append(
            {"name": f"task_{i}", "resources": [f"res_{i}"], "profit": float(i)}
        )
    resp = await client.post("/tasks/", json={"tasks": tasks}, timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 50
    assert data["total_profit"] == sum(range(50))


async def test_exact_solver_at_threshold(client):
    tasks = []
    for i in range(20):
        tasks.append({"name": f"task_{i}", "resources": [f"res_{i}"], "profit": 1.0})
    resp = await client.post("/tasks/", json={"tasks": tasks}, timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 20
    assert data["total_profit"] == 20.0


async def test_exact_solver_one_over_threshold(client):
    tasks = []
    for i in range(21):
        tasks.append({"name": f"task_{i}", "resources": [f"res_{i}"], "profit": 1.0})
    resp = await client.post("/tasks/", json={"tasks": tasks}, timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 21
    assert data["total_profit"] == 21.0


async def test_duplicate_tasks_same_resources(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "dup", "resources": ["disk"], "profit": 5.0},
                {"name": "dup", "resources": ["disk"], "profit": 5.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert len(data["buffered"]) == 1


async def test_many_resources_per_task(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {
                    "name": "heavy",
                    "resources": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
                    "profit": 3.0,
                },
                {"name": "light_1", "resources": ["a"], "profit": 2.0},
                {"name": "light_2", "resources": ["b"], "profit": 2.0},
                {"name": "light_3", "resources": ["c"], "profit": 2.0},
                {"name": "light_4", "resources": ["d"], "profit": 2.0},
                {"name": "light_5", "resources": ["e"], "profit": 2.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_profit"] == 10.0
    assert len(data["scheduled"]) == 5


async def test_tie_breaking_equal_profit(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "alpha", "resources": ["disk"], "profit": 5.0},
                {"name": "beta", "resources": ["disk"], "profit": 5.0},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scheduled"]) == 1
    assert len(data["buffered"]) == 1
    assert data["total_profit"] == 5.0


async def test_profit_precision(client):
    resp = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "precise_1", "resources": ["a"], "profit": 0.1},
                {"name": "precise_2", "resources": ["b"], "profit": 0.2},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert abs(data["total_profit"] - 0.3) < 1e-9


async def test_list_buffered_tasks(client):
    await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "winner", "resources": ["disk"], "profit": 10.0},
                {"name": "loser", "resources": ["disk"], "profit": 1.0},
            ]
        },
    )
    resp = await client.get("/tasks/?status=buffered")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "loser"
    assert data[0]["status"] == "buffered"


async def test_delete_then_check_list(client):
    create = await client.post(
        "/tasks/",
        json={"tasks": [{"name": "will delete", "resources": ["x"], "profit": 1.0}]},
    )
    task_id = create.json()["scheduled"][0]["id"]
    await client.delete(f"/tasks/{task_id}")
    resp = await client.get("/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_delete_buffered_task(client):
    create = await client.post(
        "/tasks/",
        json={
            "tasks": [
                {"name": "keep", "resources": ["disk"], "profit": 10.0},
                {"name": "remove", "resources": ["disk"], "profit": 1.0},
            ]
        },
    )
    data = create.json()
    buffered = data["buffered"]
    assert len(buffered) == 1
    await client.delete(f"/tasks/{buffered[0]['id']}")
    scheduled_resp = await client.get("/tasks/?status=scheduled")
    assert len(scheduled_resp.json()) == 1
    assert scheduled_resp.json()[0]["name"] == "keep"


async def test_concurrent_submissions(client):
    await client.post(
        "/tasks/",
        json={"tasks": [{"name": "first", "resources": ["disk"], "profit": 1.0}]},
    )
    resp = await client.post(
        "/tasks/",
        json={"tasks": [{"name": "second", "resources": ["disk"], "profit": 2.0}]},
    )
    data = resp.json()
    scheduled_names = {t["name"] for t in data["scheduled"]}
    assert "second" in scheduled_names
    all_resp = await client.get("/tasks/")
    assert len(all_resp.json()) == 2
