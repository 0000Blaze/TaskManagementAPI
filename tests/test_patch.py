from datetime import date, timedelta

def test_patch_partial_update(client):
    payload = {
        "title": "Original",
        "priority": 2,
        "due_date": (date.today() + timedelta(days=3)).isoformat(),
        "tags": ["work"]
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    task = r.json()

    r2 = client.patch(f"/tasks/{task['id']}", json={"title": "Updated"})
    assert r2.status_code == 200
    updated = r2.json()
    assert updated["title"] == "Updated"
    assert updated["priority"] == 2  # unchanged
    assert updated["tags"] == ["work"]  # unchanged

def test_patch_replace_tags(client):
    r = client.post("/tasks", json={"title":"TagReplace","priority":3,"tags":["a"]})
    assert r.status_code == 201
    tid = r.json()["id"]

    r2 = client.patch(f"/tasks/{tid}", json={"tags":["b","c"]})
    assert r2.status_code == 200
    assert set(r2.json()["tags"]) == {"b","c"}

def test_patch_due_date_past_fails(client):
    r = client.post("/tasks", json={"title":"DueTest","priority":3})
    tid = r.json()["id"]
    r2 = client.patch(f"/tasks/{tid}", json={"due_date": (date.today() - timedelta(days=1)).isoformat()})
    assert r2.status_code == 422
