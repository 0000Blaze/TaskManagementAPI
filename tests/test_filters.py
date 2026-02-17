from datetime import date, timedelta

def _create(client, title, priority, tags):
    payload = {
        "title": title,
        "priority": priority,
        "due_date": (date.today() + timedelta(days=2)).isoformat(),
        "tags": tags
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

def test_filter_by_priority(client):
    _create(client, "t1", 5, ["work"])
    _create(client, "t2", 3, ["home"])
    r = client.get("/tasks?priority=5")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert all(item["priority"] == 5 for item in data["items"])

def test_filter_by_tags_any(client):
    _create(client, "tag1", 2, ["work", "urgent"])
    _create(client, "tag2", 2, ["home"])
    r = client.get("/tasks?tags=urgent")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any("urgent" in item["tags"] for item in data["items"])
