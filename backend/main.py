import os
from contextlib import asynccontextmanager, contextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row

'''
# Task 3: Containerize stack (PostgreSQL + Docker)
## Task 3 - STAGE 1: Connect app (secret, driver, table)

A. Database URL from Environment (.env)
'''
load_dotenv() # reads key-value pairs from .env into os.environ.
DATABASE_URL = os.getenv("DATABASE_URL") # holds the PostgreSQL connection
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is missing. Configure it in .env")

'''
B. PostgreSQL Connection Helper (psycopg 3)
    1. psycopg.connect() establishes a connection to the containerized database.
    2. The context manager automatically commits on clean exit, rolls back on error,
       and closes the connection.
'''
@contextmanager
def get_db():
    """Create a PostgreSQL connection with dict-like row access."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn

def row_to_task(row: dict) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }

TASK_COLUMNS = "id, title, done"

SEED_TASKS = [
    ("Task 1: Build first CRUD API with in-memory storage", True),
    ("Task 2: Connect CRUD API to SQLite database", True),
    ("Task 3: Containerise the project stack with Docker", False),
]

'''
C. Create Table & Seed Tasks in PostgreSQL
    1. SERIAL PRIMARY KEY generates auto-incrementing integer IDs in PostgreSQL.
    2. BOOLEAN DEFAULT FALSE stores native boolean values.
    3. Seeding occurs only when table row count is 0, preventing row duplication on restart.
    4. %s placeholders prevent SQL injection attacks.
'''
def init_db() -> None:
    """Initialize PostgreSQL tasks table and seed default tasks if empty."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # 1. Create tasks table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)

            # 2. Check row count and seed only if empty
            cur.execute("SELECT COUNT(*) FROM tasks;")
            row = cur.fetchone()
            count = row["count"] if isinstance(row, dict) else row[0]
            if count == 0:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    SEED_TASKS
                )
                print(f"✅ PostgreSQL database initialized and seeded with {len(SEED_TASKS)} tasks.")

'''
D. FastAPI lifespan
    Startup: connects to PostgreSQL and runs init_db().
    Shutdown: clean application termination.
'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing startup and shutdown routines."""
    print("Starting application: Initializing PostgreSQL database...")
    init_db()
    yield
    print("Shutting down application...")

# Initialize core FastAPI application with database lifespan
app = FastAPI(
    title="Task CRUD API (PostgreSQL + Docker)",
    version="1.3.0-alpha.2",
    description="Asynchronous RESTful CRUD service for task management using containerized PostgreSQL in Docker.",
    lifespan=lifespan
)

'''
E. Error format
    Every error is returned as {"error": "<message>"}.
    1. HTTPException (our own 400/404s) -> {"error": detail}
    2. RequestValidationError (malformed JSON, wrong types such as "done": "maybe") -> 400 instead of FastAPI's default 422
'''
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})

def task_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Task not found")

# Discovery & Health Endpoints
@app.get("/")
async def root():
    return {
        "name": "Task API (PostgreSQL + Docker)",
        "version": "3.0",
        "endpoints": ["/tasks", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

# Read all tasks from PostgreSQL database
@app.get("/tasks")
async def get_tasks():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {TASK_COLUMNS} FROM tasks ORDER BY id;")
            rows = cur.fetchall()
    return [row_to_task(row) for row in rows]

# Read a single task by ID from PostgreSQL database with 404 error handling
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {TASK_COLUMNS} FROM tasks WHERE id = %s;", (task_id,))
            row = cur.fetchone()
    if row is None:
        raise task_not_found()
    return row_to_task(row)

# Model for incoming data (request body)
class TaskCreate(BaseModel):
    title: str | None = None

@app.post("/tasks", status_code=201)
async def create_task(task_input: TaskCreate):
    # 1. Zero-trust input validation
    if not task_input.title or not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    cleaned_title = task_input.title.strip()

    # 2. Insert into PostgreSQL using RETURNING clause
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (cleaned_title, False)
            )
            row = cur.fetchone()

    # 3. Return created task with assigned ID
    return row_to_task(row)

# Model for update request body
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate):
    # 1. Validation: At least 1 field must be provided
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail="At least one field (title or done) must be provided")

    # 2. Validation: If title provided, can't be empty or whitespace
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespace")

    with get_db() as conn:
        with conn.cursor() as cur:
            # 3. Check if task exists
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
            existing_task = cur.fetchone()
            if existing_task is None:
                raise task_not_found()

            # 4. Compute new values (keep old value if field wasn't sent)
            new_title = task_update.title.strip() if task_update.title is not None else existing_task["title"]
            new_done = task_update.done if task_update.done is not None else existing_task["done"]

            # 5. Execute SQL Update in PostgreSQL
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (new_title, new_done, task_id)
            )
            row = cur.fetchone()

    return row_to_task(row)

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            if cur.rowcount == 0:
                raise task_not_found()
    return None