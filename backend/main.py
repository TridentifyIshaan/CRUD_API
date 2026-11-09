from fastapi import FastAPI, HTTPException # FastAPI class is imported
from pydantic import BaseModel # For Request Body

app = FastAPI() # instance of FastAPI class is created

# The Path Operation Decorator tells FastAPI that the function immediately below it is responsible for handling requests that go to the root path (/) using an HTTP GET operation. The Path Operation Function defines the function named root that FastAPI will execute whenever it receives a GET request to the / URL. The async keyword defines it as an asynchronous function, allowing it to handle concurrent tasks efficiently.
@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]} # FastAPI automatically converts this dictionary into a JSON response.

@app.get("/health")
async def health():
    return {"status": "ok"}

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

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

class TaskCreate(BaseModel):
    title: str | None = None

@app.post("/tasks", status_code=201)
async def create_task(task_input: TaskCreate):
    if not task_input.title or not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    new_id = max([t["id"] for t in tasks], default=0) +1
    new_task = {"id": new_id, "title": task_input.title, "done": False}
    tasks.append(new_task)
    return new_task