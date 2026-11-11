from fastapi import FastAPI, HTTPException # for api
import sqlite3 # for db
from pathlib import Path # for db path
from contextlib import asynccontextmanager # for db connections

# =============================================================================
# Task 2: CRUD API with SQLite Database Storage
# =============================================================================

# =============================================================================
# Task 2 - STAGE 0: Create Database & Lifecycle Setup
# =============================================================================

# Path to the SQLite database file (CRUD_API/database/tasks.db)
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "tasks.db"

def get_db_connection() -> sqlite3.Connection:
    """Create a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing startup and shutdown routines."""
    print("Starting application: Initializing database...")
    init_db()
    yield
    print("Shutting down application...")

# Initialize core FastAPI ASGI application instance with database lifespan
app = FastAPI(
    title="Task CRUD API (SQLite)",
    version="1.1.0-alpha.2",
    description="Asynchronous RESTful CRUD service for task management using SQLite database storage.",
    lifespan=lifespan
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
