from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from postgres_repository import PostgresTaskRepository
from supabase_client import supabase
repository = PostgresTaskRepository()
DB_NAME = "tasks.db"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


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
security = HTTPBearer(auto_error=False)


@app.get("/")
async def hello():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def yaan():
    return {"status": "ok"}


@app.get(
    "/public/info",
    summary="Public information",
    description="A public endpoint that does not require authentication."
)
async def public_info():
    return {
        "message": "This is a public endpoint."
    }


@app.get(
    "/protected/profile",
    summary="Protected profile",
    description="Requires a valid Supabase access token."
)
async def protected_profile(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    try:
        response = supabase.auth.get_user(credentials.credentials)

        user = response.user

        if user is None:
            raise Exception("User not found")

        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )


@app.get(
    "/tasks",
    summary="Get all tasks",
    description="Returns all tasks stored in PostgreSQL."
)
async def get_task():
    return repository.get_all()


@app.get(
    "/tasks/{id}",
    summary="Get a task",
    description="Returns a single task by its ID."
)
async def get_task(id: int):
    task = repository.get_by_id(id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    return task


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

    return repository.create(task.title.strip())


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

    existing_task = repository.get_by_id(id)

    if existing_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    new_title = (
        task.title.strip()
        if task.title is not None
        else existing_task["title"]
    )

    new_done = (
        task.done
        if task.done is not None
        else existing_task["done"]
    )

    return repository.update(
        id,
        new_title,
        new_done
    )


@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete a task",
    description="Deletes a task by its ID."
)
async def delete_task(id: int):

    deleted = repository.delete(id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    return


@app.post(
    "/auth/signup",
    status_code=201,
    summary="Create a new account",
    description="Creates a new user account using Supabase Auth."
)
async def signup(data: SignupRequest):
    if not data.email or not data.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )
    try:
        response = supabase.auth.sign_up(
            {
                "email": str(data.email),
                "password": data.password
            }
        )
        return {
            "user": response.user
        }
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Unable to create account"}
        )


@app.post(
    "/auth/login",
    summary="Login to an existing account",
    description="Authenticates a user using Supabase Auth."
)
async def login(data: LoginRequest):

    if not data.email or not data.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": str(data.email),
                "password": data.password
            }
        )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )
