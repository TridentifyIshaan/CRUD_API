from fastapi import FastAPI, HTTPException # for api
from pydantic import BaseModel # for request body validation

# Task 1: CRUD API with In-Memory Storage
# Task 1 - STAGE 0: Application Initialization

# Initialize the core FastAPI ASGI application instance.
app = FastAPI(
    title="Task CRUD API (In-Memory)",
    version="1.0.0",
    description="Asynchronous RESTful CRUD service for task management using in-memory store."
)

# Task 1 - STAGE 1: Root & Health Endpoints

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

# Task 1 - STAGE 2: Read Operations (In-Memory Store & Lookup with 404)

# In-memory data store seeded with initial engineering internship tasks.
tasks = [
    {
        "id": 1, 
        "title": "Task 1: Build CRUD API with in-memory storage", 
        "done": True
    },
    {
        "id": 2, 
        "title": "Task 2: Connect CRUD API to SQLite database", 
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

# Task 1 - STAGE 3: Create Operation (POST with Pydantic Validation & 201 Created)

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

# Task 1 - STAGE 4: Update & Delete Operations (PUT & DELETE with 204 No Content)

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