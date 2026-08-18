from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

DB_NAME = "tasks.db"


def get_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = get_db()
    conn.execute(""" CREATE TABLE IF NOT EXISTS tasks(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT NOT NULL,
                     done INTEGER NOT NULL)
                      """)
    conn.commit()
    conn.close()


def seed_tasks():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        example_tasks = [
            ("Learn FastAPI", 0),
            ("Build CRUD API", 0),
            ("Push project to GitHub", 0)
        ]
        conn.executemany(
            "INSERT INTO tasks(title,done)VALUES (?,?)", example_tasks)
        conn.commit()
    conn.close()


create_table()
seed_tasks()


class taskcreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0.0"
)


@app.get("/")
async def hello():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def yaan():
    return {"status": "ok"}


@app.get(
    "/tasks",
    summary="Get all tasks",
    description="Returns all tasks stored in memory."
)
async def get_task():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    tasks = []
    for row in rows:
        tasks.append({"id": row[0],
                      "title": row[1],
                      "done": bool(row[2])})
    return tasks


@app.get(
    "/tasks/{id}",
    summary="Get a task",
    description="Returns a single task by its ID."
)
async def get_task(id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks where id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"id {id} not found ")
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task with a title."
)
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


@app.put(
    "/tasks/{id}",
    summary="Update a task",
    description="Updates the title and/or completion status of a task."
)
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


@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete a task",
    description="Deletes a task by its ID."
)
async def delete_task(id: int):
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )
