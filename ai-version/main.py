from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Task API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# In-memory task datastore
tasks_db = [
    {"id": 1, "title": "Setup development environment", "done": True},
    {"id": 2, "title": "Design REST API schema", "done": True},
    {"id": 3, "title": "Write automated test suite", "done": False},
]

# Pydantic validation schemas
class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

# Root & Health Endpoints
@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

# Read Operations
@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_single_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task

# Create Operation
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

# Update Operation
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

# Delete Operation
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

