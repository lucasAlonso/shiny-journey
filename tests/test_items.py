async def test_create_item(client):
    resp = await client.post("/items/", json={"name": "Test Item"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Item"
    assert "id" in data


async def test_list_items(client):
    await client.post("/items/", json={"name": "Item 1"})
    await client.post("/items/", json={"name": "Item 2"})
    resp = await client.get("/items/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_get_item(client):
    create_resp = await client.post("/items/", json={"name": "Test"})
    item_id = create_resp.json()["id"]
    resp = await client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test"


async def test_get_item_not_found(client):
    resp = await client.get("/items/999")
    assert resp.status_code == 404


async def test_delete_item(client):
    create_resp = await client.post("/items/", json={"name": "Delete Me"})
    item_id = create_resp.json()["id"]
    resp = await client.delete(f"/items/{item_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404
