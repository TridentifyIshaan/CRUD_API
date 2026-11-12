from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from typing import Optional, List

# =============================================================================
# Task 1 - STAGE 7: The AI Rematch (Quarantined AI-Generated Implementation)
# =============================================================================
# Quarantined LLM generation benchmarked against the hand-crafted implementation.

# =============================================================================
# Task 1 - STAGE 0: Application Initialization
# =============================================================================
# Core FastAPI ASGI instance configured with interactive documentation routes.
app = FastAPI(
    title="Task API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# Task 1 - STAGE 1: Discovery & Health Endpoints
# =============================================================================
# Root endpoint providing service discovery metadata.
@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health"]
    }

# Health check probe for liveness and monitoring verification.
@app.get("/health")
def get_health():
    return {"status": "ok"}

# =============================================================================
# Task 1 - STAGE 2: Read Operations (In-Memory Store & Lookup with 404)
# =============================================================================
# In-memory task datastore seeded with initial demo tasks.
tasks_db = [
    {"id": 1, "title": "Setup development environment", "done": True},
    {"id": 2, "title": "Design REST API schema", "done": True},
    {"id": 3, "title": "Write automated test suite", "done": False},
]

# Response serialization model for task objects.
class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

# Retrieve the complete task collection.
@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks():
    return tasks_db

# Retrieve a single task by ID or return 404 Not Found.
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_single_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task

# =============================================================================
# Task 1 - STAGE 3: Create Operation (POST with Pydantic Validation & 201 Created)
# =============================================================================
# Request body validation schema for task creation.
class TaskCreate(BaseModel):
    title: Optional[str] = None

# Create a task, auto-assign ID, enforce validation rules, and return HTTP 201.
@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required and cannot be empty"
        )
    
    new_id = (max(t["id"] for t in tasks_db) if tasks_db else 0) + 1
    new_task = {
        "id": new_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks_db.append(new_task)
    return new_task

# =============================================================================
# Task 1 - STAGE 4: Update & Delete Operations (PUT & DELETE with 204 No Content)
# =============================================================================
# Request body validation schema for partial updates.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# Update task title and/or done status with validation and 404 handling.
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide title or done to update"
        )
    
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        task["title"] = payload.title.strip()
    
    if payload.done is not None:
        task["done"] = payload.done
        
    return task

# Delete task by ID and return HTTP 204 No Content.
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

