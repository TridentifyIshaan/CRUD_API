from fastapi import FastAPI, HTTPException # FastAPI class is imported

app = FastAPI() # instance of FastAPI class is created

# The Path Operation Decorator tells FastAPI that the function immediately below it is responsible for handling requests that go to the root path (/) using an HTTP GET operation. The Path Operation Function defines the function named root that FastAPI will execute whenever it receives a GET request to the / URL. The async keyword defines it as an asynchronous function, allowing it to handle concurrent tasks efficiently.
@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]} # FastAPI automatically converts this dictionary into a JSON response.

@app.get("/health")
async def health():
    return {"status": "ok"}

tasks = [
    {"id": 1, "title": "Complete Stage 0", "done": True},
    {"id": 2, "title": "Complete Stage 1", "done": True},
    {"id": 3, "title": "Complete Stage 2", "done": True},
    {"id": 4, "title": "Complete Stage 3", "done": False},
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