from datetime import date, timedelta

def test_create_task_success(client):
    payload = {
        "title": "Pay bills",
        "description": "Electricity and internet",
        "priority": 4,
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "tags": ["Work", "Urgent"]
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Pay bills"
    assert data["priority"] == 4
    assert set(data["tags"]) == {"work", "urgent"}

def test_create_task_validation_priority(client):
    payload = {"title": "Bad", "priority": 6}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422
    assert r.json()["error"] == "Validation Failed"

def test_create_task_validation_due_date_past(client):
    payload = {"title": "Past", "priority": 3, "due_date": (date.today() - timedelta(days=1)).isoformat()}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "Validation Failed"
