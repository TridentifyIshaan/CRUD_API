"""Task 3 - STAGE 6: AI vs Me (quarantined AI-generated Postgres + Docker stack).

AI-generated migration of the Task API from SQLite to containerized PostgreSQL,
kept in quarantine and benchmarked against the hand-built backend/main.py.
Round 2 (rematch): regenerated from the improved prompt in the README —
/health returns exactly {"status": "ok"} and Postgres is not published to the
host. Round 1 is preserved at git tag v1.3.0.
Runs with its own compose file (ai-version/compose.yaml), API port 8001 and
its own volume, so it never touches the hand-built stack. Task 2's AI version is preserved in ai-version/task2_main.py.

Run: docker compose -f ai-version/compose.yaml --env-file .env up --build
"""
import os
from contextlib import asynccontextmanager, contextmanager
from typing import List, Optional

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from pydantic import BaseModel

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (copy .env.example to .env)")

SEED_TASKS = [
    ("Task 1: Build first CRUD API with in-memory storage", True),
    ("Task 2: Connect CRUD API to SQLite database", True),
    ("Task 3: Containerise the project stack with Docker", False),
]


# --- Repository: every database line lives below --------------------------------
@contextmanager
def get_connection():
    # psycopg's connection context manager commits on success, rolls back on
    # error and closes the connection.
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn


def init_db() -> None:
    with get_connection() as conn:  # one transaction: create + seed together
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    SERIAL  PRIMARY KEY,
                title TEXT    NOT NULL CHECK (length(trim(title)) > 0),
                done  BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        # Serialize concurrent starts so two replicas can't both seed.
        conn.execute("LOCK TABLE tasks IN EXCLUSIVE MODE")
        count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
        if count == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)", SEED_TASKS
                )


def db_list() -> list:
    with get_connection() as conn:
        return conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()


def db_get(task_id: int) -> Optional[dict]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()


def db_create(title: str) -> dict:
    with get_connection() as conn:
        return conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, False),
        ).fetchone()


def db_update(task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[dict]:
    with get_connection() as conn:
        # COALESCE keeps the stored value for fields the client did not send.
        return conn.execute(
            "UPDATE tasks SET title = COALESCE(%s, title), done = COALESCE(%s, done) "
            "WHERE id = %s RETURNING id, title, done",
            (title, done, task_id),
        ).fetchone()


def db_delete(task_id: int) -> bool:
    with get_connection() as conn:
        return conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,)).rowcount > 0


# --- HTTP layer -----------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API (PostgreSQL, AI version)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid request body"}
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


def not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.get("/")
async def get_root():
    return {
        "name": "Task API (PostgreSQL, AI version)",
        "version": "3.0",
        "endpoints": ["/tasks", "/health"],
    }


@app.get("/health")
async def get_health():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks():
    return db_list()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_single_task(task_id: int):
    row = db_get(task_id)
    if row is None:
        raise not_found()
    return row


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required and cannot be empty",
        )
    return db_create(payload.title.strip())


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide title or done to update",
        )
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty"
        )
    title = payload.title.strip() if payload.title is not None else None
    row = db_update(task_id, title, payload.done)
    if row is None:
        raise not_found()
    return row


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    if not db_delete(task_id):
        raise not_found()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
