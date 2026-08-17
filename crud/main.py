from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class taskcreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


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


@app.post("/tasks", status_code=201)
async def create_task(task: taskcreate):
    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="TITLE CAN NOT BE EMPTY"
        )
    new_task = {
        "id": len(tasks)+1,
        "title": task.title,
        "done": False}
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{id}")
async def update_task(id: int, task: TaskUpdate):
    for existing_task in tasks:
        if existing_task["id"] == id:

            if task.title is not None:
                if not task.title.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )
                existing_task["title"] = task.title

            if task.done is not None:
                existing_task["done"] = task.done

            return existing_task

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )


@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )
