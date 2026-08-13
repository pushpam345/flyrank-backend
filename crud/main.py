from fastapi import FastAPI, HTTPException
app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Push project to GitHub", "done": False}
]


@app.get("/")
async def hello():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def yaan():
    return {"status": "ok"}


@app.get("/tasks")
async def task():
    return {"tasks": tasks}


@app.get("/tasks/{id}")
async def taskget(id: int):

    for i in tasks:
        if i["id"] == id:
            return i
    raise HTTPException(status_code=404, detail=f"id {id} not found ")
