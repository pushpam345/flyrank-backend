from fastapi import FastAPI
from fastapi.responses import JSONResponse

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
    description="Returns all tasks stored in SQLite."
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
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
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
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks(title, done) VALUES (?,?) ", (task.title.strip(), 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {
        "id": new_id,
        "title": task.title.strip(),
        "done": False
    }


@app.put(
    "/tasks/{id}",
    summary="Update a task",
    description="Updates the title and/or completion status of a task."
)
async def update_task(id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )
    if task.title is not None and not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )
    conn = get_db()
    existing_task = conn.execute(
        "SELECT * FROM tasks where id =?", (id,)).fetchone()
    if existing_task is None:
        conn.close()

        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    new_title = (
        task.title.strip()
        if task.title is not None
        else existing_task[1]
    )

    new_done = (
        int(task.done)
        if task.done is not None
        else existing_task[2]
    )
    conn.execute(''' UPDATE tasks 
    SET title =? , done= ?
    WHERE id=?''', (new_title, new_done, id))
    conn.commit()
    updated_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return {
        "id": updated_task[0],
        "title": updated_task[1],
        "done": bool(updated_task[2])
    }


@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete a task",
    description="Deletes a task by its ID."
)
async def delete_task(id: int):

    conn = get_db()

    # Check whether task exists
    existing_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    if existing_task is None:
        conn.close()

        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    # Delete task
    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return
