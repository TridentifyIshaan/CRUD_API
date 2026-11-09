from fastapi import FastAPI # FastAPI class is imported

app = FastAPI() # instance of FastAPI class is created

# The Path Operation Decorator tells FastAPI that the function immediately below it is responsible for handling requests that go to the root path (/) using an HTTP GET operation. The Path Operation Function defines the function named root that FastAPI will execute whenever it receives a GET request to the / URL. The async keyword defines it as an asynchronous function, allowing it to handle concurrent tasks efficiently.
@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]} # FastAPI automatically converts this dictionary into a JSON response.

@app.get("/health")
async def health():
    return {"status": "ok"}