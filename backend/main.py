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
    title="Task CRUD API",
    version="1.1.0-alpha.1",
    description="Asynchronous RESTful CRUD service for task management.",
    lifespan=lifespan #lifespan function
)

# =============================================================================
# Task 1: CRUD API with In-Memory Storage (Legacy Stages 0 to 7)
# =============================================================================

# =============================================================================
# Task 1 - STAGE 0: Application Initialization [SUPERSEDED BY TASK 2 STAGE 0]
# =============================================================================
# The original base FastAPI app without database lifespan initialization is
# commented out below because Task 2 Stage 0 initializes 'app' above with lifespan.
#
# app = FastAPI(
#     title="Task CRUD API",
#     version="1.0.0",
#     description="Asynchronous RESTful CRUD service for task management."
# )

# =============================================================================
# Task 1 - STAGE 1: Root & Health Endpoints
# =============================================================================
# Root endpoint returning API metadata and service discovery details.
@app.get("/")
async def root():
    return {
        "name": "Task API", 
        "version": "1.0", 
        "endpoints": ["/tasks", "/health"]
    }

# Health probe endpoint used by monitoring services to verify service availability.
@app.get("/health")
async def health():
    return {"status": "ok"}

# =============================================================================
# Task 1 - STAGE 2: Read Operations (In-Memory Store & Lookup with 404)
# =============================================================================
# In-memory data store seeded with initial engineering internship tasks.
tasks = [
    {
        "id": 1, 
        "title": "Complete onboarding & configure local development environment", 
        "done": True
    },
    {
        "id": 2, 
        "title": "Review REST API design specifications and HTTP status code standards", 
        "done": True
    },
    {
        "id": 3, 
        "title": "Implement core CRUD endpoints with Pydantic validation", 
        "done": False
    },
    {
        "id": 4, 
        "title": "Document API contracts in Swagger UI and submit pull request for review", 
        "done": False
    },
]

# Read all tasks in the system.
@app.get("/tasks")
async def get_tasks():
    return tasks

# Read a single task by ID with path parameter validation and 404 error handling.
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# =============================================================================
# Task 1 - STAGE 3: Create Operation (POST with Pydantic Validation & 201 Created)
# =============================================================================
# Request body schema for creating a task (title validation).
class TaskCreate(BaseModel):
    title: str | None = None

# Create a new task with input validation and automated ID allocation.
@app.post("/tasks", status_code=201)
async def create_task(task_input: TaskCreate):
    # Validate that title exists and is not whitespace
    if not task_input.title or not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    
    # Calculate next available ID safely
    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id, 
        "title": task_input.title.strip(), 
        "done": False
    }
    tasks.append(new_task)
    return new_task

# =============================================================================
# Task 1 - STAGE 4: Update & Delete Operations (PUT & DELETE with 204 No Content)
# =============================================================================
# Request body schema for updating task fields (title, done status, or both).
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

# Update an existing task's title and/or completion status.
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            # Ensure at least one field is provided for update
            if task_update.title is None and task_update.done is None:
                raise HTTPException(status_code=400, detail="Must provide title or done to update")

            # Validate and update title if provided
            if task_update.title is not None:
                if not task_update.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = task_update.title.strip()

            # Update done status if provided
            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Delete a task by ID and return HTTP 204 No Content with an empty body.
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return None
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

