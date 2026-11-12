from fastapi import FastAPI, HTTPException # for api
from pydantic import BaseModel # for request body validation
import sqlite3 # for db
from pathlib import Path # for db path
from contextlib import asynccontextmanager # for db connections

# =============================================================================
# Task 2: CRUD API with SQLite Database Storage
# =============================================================================

# =============================================================================
# Task 2 - STAGE 0: Create Database & Lifecycle Setup
# =============================================================================

'''
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
    1. conn = sqlite3.connect(DB_PATH) creates a connection to the database.
    2. conn.row_factory = sqlite3.Row allows us to access rows as dictionaries to make search easy.
'''
def get_db_connection() -> sqlite3.Connection:
    """Create a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

'''
C. Create Table & Seed Tasks
    1. DB_PATH.parent refers to database/ folder.
    2. mkdir() creates the folder if it doesn't exist.
    3. parents=True allows us to create parent directories if they don't exist. 
    4. exist_ok=True prevents an error if the folder already exists.
    5. get_db_connection() creates a connection to the database.
    6. cursor = conn.cursor() creates a cursor to execute SQL commands.
    7. with keyword is used for automatic closure of the database connection.
    8. 0 means False, 1 means True
    9. fetchone()[0] retrieves the first row's first column(count of tasks).
    10. VALUES (?, ?) placeholder prevents SQL injection attacks.
'''
def init_db() -> None:
    """Initialize table and seed default tasks if empty."""
    # Ensure database/ folder exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0   
            )
        """)

        # 2. Check current row count
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        # 3. Seed only when empty
        if count == 0:
            seed_tasks = [
                ("Task 1: Build your first CRUD API with in-memory storage", 1),
                ("Task 2: Connect CRUD API to SQLite database", 0),
            ]
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                seed_tasks
            )
            conn.commit()
            print("✅ Database initialized and seeded with 2 tasks.")

'''
D. FastAPI lifespan
    1. @asynccontextmanager decorator allows us to use lifespan in the FastAPI constructor.
    2. yield: when application is starting up, init_db() runs, and the application pauses at yield until all startup tasks are completed.
    3. After the application is running, the code after yield will run when the application is shutting down.
'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing startup and shutdown routines."""
    print("Starting application: Initializing database...")
    init_db()
    yield
    print("Shutting down application...")

# Initialize core FastAPI ASGI (Asynchronous Server Gateway Interface) application instance with database lifespan
app = FastAPI(
    title="Task CRUD API (SQLite)",
    version="1.1.0-alpha.3",
    description="Asynchronous RESTful CRUD service for task management using SQLite database storage.",
    lifespan=lifespan #lifespan function
)

# =============================================================================
# Discovery & Health Endpoints
# =============================================================================
@app.get("/")
async def root():
    return {
        "name": "Task API (Database)", 
        "version": "2.0", 
        "endpoints": ["/tasks", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

# =============================================================================
# Task 2 - STAGE 1: Database Read Endpoints
# =============================================================================
# Read all tasks from SQLite database
@app.get("/tasks")
async def get_tasks():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks")
        rows = cursor.fetchall()
        return [
            {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
            for row in rows
        ]

# Read a single task by ID from SQLite database with 404 error handling
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

# =============================================================================
# Task 2 - STAGE 2: Create New Tasks (INSERT into SQLite)
# =============================================================================
# Model for incoming data (request body)
class TaskCreate(BaseModel):
    title: str | None = None

@app.post("/tasks", status_code=201)
async def create_task(task_input: TaskCreate):
    # 1. Zero-trust input validation
    if not task_input.title or not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required & can't be empty")
    cleaned_title = task_input.title.strip()

    # 2. Insert into database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (cleaned_title, 0)
        )
        conn.commit()
        new_id = cursor.lastrowid

    # 3. Return created task with assigned ID
    return {
        "id": new_id,
        "title": cleaned_title,
        "done": False
    }
