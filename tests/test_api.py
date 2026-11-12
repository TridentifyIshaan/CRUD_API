"""Endpoint tests shared by Task 1 (in-memory) and Task 2 (SQLite).

The same contract tests run against both backends: if they pass on both,
the storage layer really is just an implementation detail.

Run: uv run pytest
"""
import importlib.util
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
CORE = {"id", "title", "done"}


def load(relative_path: str, db_path: Path | None = None):
    """Import a fresh copy of an app module (fresh in-memory list / chosen db file)."""
    spec = importlib.util.spec_from_file_location(f"app_{abs(hash((relative_path, str(db_path))))}", ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if db_path is not None:
        module.DB_PATH = db_path
    return module


@pytest.fixture(params=["backend/task1_main.py", "backend/main.py"], ids=["task1-memory", "task2-sqlite"])
def client(request, tmp_path):
    db = tmp_path / "database" / "tasks.db" if request.param == "backend/main.py" else None
    with TestClient(load(request.param, db).app) as c:
        yield c


def core(task: dict) -> dict:
    return {k: task[k] for k in CORE}


def assert_error(response, code: int):
    assert response.status_code == code
    body = response.json()
    assert isinstance(body, dict) and len(body) == 1  # one JSON error message


# ---------------- Contract tests: identical for Task 1 and Task 2 ----------------

def test_health_and_root(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert "/tasks" in client.get("/").json()["endpoints"]


def test_list_seeded_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks and all(CORE <= t.keys() for t in tasks)


def test_get_one_and_unknown(client):
    first = client.get("/tasks").json()[0]
    assert core(client.get(f"/tasks/{first['id']}").json()) == core(first)
    assert_error(client.get("/tasks/999"), 404)


@pytest.mark.parametrize("body", [{}, {"title": ""}, {"title": "   "}])
def test_create_rejects_blank_title(client, body):
    assert_error(client.post("/tasks", json=body), 400)


def test_full_crud_lifecycle(client):
    created = client.post("/tasks", json={"title": "  Write tests  "})
    assert created.status_code == 201
    task = created.json()
    assert core(task) == {"id": task["id"], "title": "Write tests", "done": False}

    updated = client.put(f"/tasks/{task['id']}", json={"done": True})
    assert updated.status_code == 200
    assert core(updated.json()) == {"id": task["id"], "title": "Write tests", "done": True}

    renamed = client.put(f"/tasks/{task['id']}", json={"title": "Renamed"})
    assert core(renamed.json()) == {"id": task["id"], "title": "Renamed", "done": True}

    assert_error(client.put(f"/tasks/{task['id']}", json={}), 400)
    assert_error(client.put(f"/tasks/{task['id']}", json={"title": "  "}), 400)
    assert_error(client.put("/tasks/999", json={"done": True}), 404)

    deleted = client.delete(f"/tasks/{task['id']}")
    assert deleted.status_code == 204 and deleted.content == b""
    assert_error(client.get(f"/tasks/{task['id']}"), 404)
    assert_error(client.delete(f"/tasks/{task['id']}"), 404)


# ---------------- Task 2 only: persistence, seeding, errors, extras ----------------

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "database" / "tasks.db"


def start(db_path):
    return TestClient(load("backend/main.py", db_path).app)


def test_db_created_and_seeded_once(db_path):
    for _ in range(3):  # three restarts
        with start(db_path) as c:
            assert len(c.get("/tasks").json()) == 3
    assert db_path.exists()


def test_data_survives_restart(db_path):
    with start(db_path) as c:
        new_id = c.post("/tasks", json={"title": "Persist me"}).json()["id"]
        c.put("/tasks/1", json={"done": False})
    with start(db_path) as c:
        assert c.get(f"/tasks/{new_id}").json()["title"] == "Persist me"
        assert c.get("/tasks/1").json()["done"] is False


def test_error_format(db_path):
    with start(db_path) as c:
        assert c.get("/tasks/999").json() == {"error": "Task not found"}
        assert c.post("/tasks", json={}).json() == {"error": "Title is required and cannot be empty"}
        bad = c.put("/tasks/1", json={"done": "maybe"})  # wrong type -> 400, not 422
        assert bad.status_code == 400 and "error" in bad.json()


def test_filter_search_sort(db_path):
    with start(db_path) as c:
        c.post("/tasks", json={"title": "alpha CRUD"})
        done = c.get("/tasks", params={"done": "true"}).json()
        assert done and all(t["done"] for t in done)
        assert all(not t["done"] for t in c.get("/tasks", params={"done": "false"}).json())
        assert [t["title"] for t in c.get("/tasks", params={"search": "crud"}).json()] == [
            "Task 1: Build CRUD API with in-memory storage",
            "Task 2: Connect CRUD API to SQLite database",
            "alpha CRUD",
        ]
        titles = [t["title"] for t in c.get("/tasks", params={"sort": "title"}).json()]
        assert titles == sorted(titles, key=str.lower)
        assert c.get("/tasks", params={"sort": "nope"}).status_code == 400
        # search value is bound as a parameter, so SQL in it is just text
        assert c.get("/tasks", params={"search": "' OR 1=1 --"}).json() == []


def test_stats(db_path):
    with start(db_path) as c:
        assert c.get("/stats").json() == {"total": 3, "done": 2, "pending": 1}
        c.post("/tasks", json={"title": "one more"})
        assert c.get("/stats").json() == {"total": 4, "done": 2, "pending": 2}


def test_timestamps(db_path):
    with start(db_path) as c:
        task = c.post("/tasks", json={"title": "stamped"}).json()
        assert task["created_at"] and task["updated_at"]
        assert c.put(f"/tasks/{task['id']}", json={"done": True}).json()["created_at"] == task["created_at"]


def test_migrates_old_schema(db_path):
    """A tasks.db created before timestamps existed gets the new columns, keeping its rows."""
    db_path.parent.mkdir(parents=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done BOOLEAN NOT NULL DEFAULT 0)")
        conn.execute("INSERT INTO tasks (title, done) VALUES ('old row', 1)")
    with start(db_path) as c:
        tasks = c.get("/tasks").json()
        assert [t["title"] for t in tasks] == ["old row"]  # not re-seeded
        assert tasks[0]["created_at"] is not None
