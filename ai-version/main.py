from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional
import sqlite3

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

# =============================================================================
# Task 2 - STAGE 6: AI vs Me (Quarantined AI-Generated SQLite Migration)
# =============================================================================
# AI-generated migration of the in-memory Task API to SQLite, kept in
# quarantine and benchmarked against the hand-built backend/main.py.
# Uses its own database file (ai-version/tasks.db) so it never touches
# the hand-built database/tasks.db.

DB_PATH = Path(__file__).resolve().parent / "tasks.db"

SEED_TASKS = [
    ("Setup development environment", 1),
    ("Design REST API schema", 1),
    ("Write automated test suite", 0),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        with conn:  # single transaction: create + seed commit together
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT    NOT NULL CHECK (length(trim(title)) > 0),
                    done  INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
                )
                """
            )
            (count,) = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
            if count == 0:
                conn.executemany(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
                )
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API (SQLite)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
    )


@app.get("/")
def get_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks", "/health"]}


@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [row_to_task(r) for r in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_single_task(task_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise not_found(task_id)
        return row_to_task(row)
    finally:
        conn.close()


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required and cannot be empty",
        )
    title = payload.title.strip()
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)", (title,)
            )
        return {"id": cur.lastrowid, "title": title, "done": False}
    finally:
        conn.close()


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide title or done to update",
        )
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty"
        )

    conn = get_connection()
    try:
        with conn:
            # COALESCE keeps the current value when a field is not supplied,
            # so the read-modify-write happens in one statement.
            cur = conn.execute(
                "UPDATE tasks SET title = COALESCE(?, title), "
                "done = COALESCE(?, done) WHERE id = ?",
                (
                    payload.title.strip() if payload.title is not None else None,
                    int(payload.done) if payload.done is not None else None,
                    task_id,
                ),
            )
            if cur.rowcount == 0:
                raise not_found(task_id)
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_task(row)
    finally:
        conn.close()


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise not_found(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    finally:
        conn.close()
