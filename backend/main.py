from fastapi import FastAPI, HTTPException, Request # for api
from fastapi.exceptions import RequestValidationError # for invalid request bodies
from fastapi.responses import JSONResponse # for custom error responses
from pydantic import BaseModel # for request body validation
import sqlite3 # for db
from pathlib import Path # for db path
from contextlib import asynccontextmanager, contextmanager # for app lifespan & db connections

'''
# Task 2: CRUD API with SQLite Database Storage
## Task 2 - STAGE 0: Create Database & Lifecycle Setup

A. Path to the SQLite database file (CRUD_API/database/tasks.db)
    1. __file__ is a special Python variable that holds the current file path.
    2. resolve() converts the file path to an absolute path.
    3. parent refers to the current directory(backend).
    4. parent.parent refers to the parent directory of the current directory(CRUD_API).
    5. / "database" / "tasks.db" uses Python's path-joining operator '/' to point to CRUD_API/database/tasks.db
'''
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "tasks.db"

'''
B. Database Connection Helper
    1. sqlite3.Row allows us to access rows as dictionaries to make search easy.
    2. Using `with get_db() as conn:` opens ONE transaction:
       - everything inside is committed together if the block succeeds,
       - everything is rolled back if any error is raised (all-or-nothing),
       - the connection is always closed afterwards (sqlite3's own `with conn` does NOT close it).
'''
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH) # creates a connection to the database
    conn.row_factory = sqlite3.Row
    try:
        with conn: # transaction: commit on success, rollback on error
            yield conn
    finally:
        conn.close()

# Converts a database row into the JSON shape returned by the API (done: 0/1 -> False/True)
def row_to_task(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

TASK_COLUMNS = "id, title, done, created_at, updated_at"

SEED_TASKS = [
    ("Task 1: Build your first CRUD API with in-memory storage", 1), # True
    ("Task 2: Connect CRUD API to SQLite database", 1), # True
    ("Task 3: Containerise the project stack with Docker", 0), # False
]

'''
C. Create Table, Migrate & Seed Tasks
    1. DB_PATH.parent refers to database/ folder; mkdir() creates it if it doesn't exist.
    2. CREATE TABLE IF NOT EXISTS only creates a missing table - it never changes an existing one.
    3. Migration: databases created before timestamps existed are missing created_at/updated_at,
       so we inspect the columns (PRAGMA table_info) and ALTER TABLE to add whatever is missing.
    4. Indexes on done & title let SQLite find filtered rows and sort by title without scanning every row.
    5. Seeding runs inside the same transaction as the count check, so the three tasks are
       inserted all-or-nothing - a crash mid-seed can never leave one or two half-seeded rows.
    6. VALUES (?, ?) placeholder prevents SQL injection attacks.
'''
def init_db() -> None:
    """Initialize table, apply migrations and seed default tasks if empty."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_db() as conn:
        # 1. Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 2. Migration: add timestamp columns to databases created before they existed
        existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        for column in ("created_at", "updated_at"):
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {column} TEXT") # fixed names, no user input
        conn.execute("UPDATE tasks SET created_at = datetime('now') WHERE created_at IS NULL")
        conn.execute("UPDATE tasks SET updated_at = created_at WHERE updated_at IS NULL")

        # 3. Indexes for the filter (done) and sort (title) queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks (done)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks (title)")

        # 4. Seed only when empty
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done, created_at, updated_at) "
                "VALUES (?, ?, datetime('now'), datetime('now'))",
                SEED_TASKS
            )
            print(f"✅ Database initialized and seeded with {len(SEED_TASKS)} tasks.")

'''
D. FastAPI lifespan
    1. yield: when application is starting up, init_db() runs, and the application pauses at yield until all startup tasks are completed.
    2. After the application is running, the code after yield will run when the application is shutting down.
'''
@asynccontextmanager # allows us to use lifespan in the FastAPI constructor
async def lifespan(app: FastAPI):
    """Application lifespan managing startup and shutdown routines."""
    print("Starting application: Initializing database...")
    init_db()
    yield
    print("Shutting down application...")

# Initialize core FastAPI ASGI (Asynchronous Server Gateway Interface) application instance with database lifespan
app = FastAPI(
    title="Task CRUD API (SQLite)",
    version="1.2.0",
    description="Asynchronous RESTful CRUD service for task management using SQLite database storage.",
    lifespan=lifespan #lifespan function
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
        "name": "Task API (Database)",
        "version": "2.0",
        "endpoints": ["/tasks", "/stats", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

# Task 2 - STAGE 1: Database Read Endpoints

'''
Read all tasks from SQLite database
    Optional extras (all filtering/sorting happens in SQL, not in a Python loop):
    1. ?done=true|false  -> WHERE done = ?
    2. ?search=CRUD      -> WHERE title LIKE ?   ('%CRUD%' matches any title containing "CRUD")
    3. ?sort=title       -> ORDER BY title (default ORDER BY id)
    Only fixed SQL fragments are joined together; user values always go through ? placeholders.
'''
@app.get("/tasks")
async def get_tasks(done: bool | None = None, search: str | None = None, sort: str = "id"):
    if sort not in ("id", "title"):
        raise HTTPException(status_code=400, detail="sort must be 'id' or 'title'")

    conditions, params = [], []
    if done is not None:
        conditions.append("done = ?")
        params.append(int(done))
    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    query = f"SELECT {TASK_COLUMNS} FROM tasks"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY title COLLATE NOCASE, id" if sort == "title" else " ORDER BY id"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_task(row) for row in rows]

# Read a single task by ID from SQLite database with 404 error handling
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    with get_db() as conn:
        row = conn.execute(f"SELECT {TASK_COLUMNS} FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise task_not_found()
    return row_to_task(row)

# Extra: statistics computed by SQL (COUNT/SUM) instead of counting in Python
@app.get("/stats")
async def get_stats():
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(done), 0) AS done FROM tasks"
        ).fetchone()
    return {"total": row["total"], "done": row["done"], "pending": row["total"] - row["done"]}

# Task 2 - STAGE 2: Create New Tasks (INSERT into SQLite)

# Model for incoming data (request body)
class TaskCreate(BaseModel):
    title: str | None = None

@app.post("/tasks", status_code=201)
async def create_task(task_input: TaskCreate):
    # 1. Zero-trust input validation
    if not task_input.title or not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    cleaned_title = task_input.title.strip()

    # 2. Insert into database (timestamps set by SQLite)
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done, created_at, updated_at) "
            "VALUES (?, ?, datetime('now'), datetime('now'))",
            (cleaned_title, 0)
        )
        row = conn.execute(f"SELECT {TASK_COLUMNS} FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()

    # 3. Return created task with assigned ID
    return row_to_task(row)

# Task 2 - STAGE 3: Update and Delete with SQL
# --------- UPDATE ---------

# None = None allows partial updates where that field is optional
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate):
    # 1. Validation: Atleast 1 field must be provided
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail="At least one field (title or done) must be provided")

    # 2. Validation: If title provided, can't be empty or whitespace
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespace")

    with get_db() as conn:
        # 3. Check if task exists in SQLite
        existing_task = conn.execute("SELECT title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing_task is None:
            raise task_not_found()

        # 4. Compute new values (keep old value if field wasn't sent)
        new_title = task_update.title.strip() if task_update.title is not None else existing_task["title"]
        new_done = int(task_update.done) if task_update.done is not None else existing_task["done"]

        # 5. Execute SQL Update (read + write in one transaction) and refresh updated_at
        conn.execute(
            "UPDATE tasks SET title = ?, done = ?, updated_at = datetime('now') WHERE id = ?",
            (new_title, new_done, task_id)
        )
        row = conn.execute(f"SELECT {TASK_COLUMNS} FROM tasks WHERE id = ?", (task_id,)).fetchone()

    return row_to_task(row)

# --------- DELETE ---------
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    # If no row was deleted, ID was not found
    if cursor.rowcount == 0:
        raise task_not_found()
    return None
