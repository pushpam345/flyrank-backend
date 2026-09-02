# Task API

A simple CRUD REST API built with FastAPI, PostgreSQL, and Docker Compose.

The project was developed progressively across three stages:

- **A1:** In-memory task storage
- **A2:** SQLite database storage
- **A3:** PostgreSQL running in Docker with a repository layer and persistent Docker volume

In A3, the application was migrated from SQLite to PostgreSQL while keeping the API behavior unchanged.

---

## Tech Stack

- Python
- FastAPI
- Pydantic
- PostgreSQL 17
- Psycopg 3
- Docker
- Docker Compose
- SQLite (used in A2)

---

## Project Structure

```text
flyrank-backend/
│
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── schema.sql
├── README.md
│
└── task-api/
    ├── main.py
    ├── database.py
    ├── repository.py
    ├── postgres_repository.py
    ├── Dockerfile
    └── requirements.txt
```

### Important Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI application and API routes |
| `database.py` | PostgreSQL connection handling |
| `repository.py` | Repository interface for task operations |
| `postgres_repository.py` | PostgreSQL implementation of the repository |
| `schema.sql` | SQL schema for the `tasks` table |
| `Dockerfile` | Docker image configuration for FastAPI |
| `docker-compose.yml` | Runs FastAPI and PostgreSQL together |
| `.env` | Local environment configuration |
| `.env.example` | Safe environment configuration template |
| `.gitignore` | Prevents secrets and local files from being committed |

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns API information |
| GET | `/health` | Health check |
| GET | `/tasks` | Returns all tasks |
| GET | `/tasks/{id}` | Returns a task by ID |
| POST | `/tasks` | Creates a new task |
| PUT | `/tasks/{id}` | Updates a task |
| DELETE | `/tasks/{id}` | Deletes a task |

---

# API Documentation

FastAPI automatically provides interactive Swagger documentation.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to test all CRUD endpoints.

---

# Database

## A2 - SQLite

In A2, the application used SQLite as its persistent database.

The database was stored locally in:

```text
tasks.db
```

The SQLite implementation provided:

- Table creation
- Seed data
- Read operations
- Insert operations
- Update operations
- Delete operations

SQLite was used as an intermediate step before migrating to PostgreSQL.

---

# A3 - PostgreSQL

In A3, SQLite was replaced with PostgreSQL.

PostgreSQL 17 runs inside a Docker container.

The database contains a `tasks` table with the following structure:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

The schema is defined in:

```text
schema.sql
```

---

# Repository Layer

The application uses a repository layer to separate database operations from the FastAPI routes.

The architecture is:

```text
Client
   |
   v
FastAPI Routes
   |
   v
Repository Interface
   |
   v
PostgresTaskRepository
   |
   v
PostgreSQL
```

The repository provides operations such as:

```text
get_all()
get_by_id()
create()
update()
delete()
```

Database-specific SQL queries are implemented inside:

```text
postgres_repository.py
```

The database connection is handled by:

```text
database.py
```

This keeps database logic separate from the API layer.

---

# Database Connection

The PostgreSQL connection string is provided through the `DATABASE_URL` environment variable.

Inside Docker Compose, the application connects to PostgreSQL using the service name:

```text
db
```

The connection string therefore uses:

```text
postgresql://taskuser:taskpassword@db:5432/tasksdb
```

The application must use `db:5432` when running inside Docker.

`localhost:5432` would refer to the FastAPI container itself and would not reach the PostgreSQL container.

---

# Environment Variables

Sensitive configuration is stored in `.env`.

Example:

```env
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
POSTGRES_DB=tasksdb
DATABASE_URL=postgresql://taskuser:taskpassword@db:5432/tasksdb
```

The `.env` file is ignored by Git and should not be committed.

A safe template is provided as:

```text
.env.example
```

Example:

```env
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=tasksdb
DATABASE_URL=postgresql://taskuser:your_password_here@db:5432/tasksdb
```

---

# Docker Compose

The complete application consists of two services:

```text
┌──────────────────────────┐
│        task-api          │
│         FastAPI          │
│        Port 8000         │
└────────────┬─────────────┘
             │
             │ db:5432
             ▼
┌──────────────────────────┐
│      task-postgres       │
│       PostgreSQL 17      │
│        Port 5432         │
└────────────┬─────────────┘
             │
             ▼
      postgres_data
       Docker Volume
```

The services communicate using the Docker Compose network.

The PostgreSQL service is named:

```text
db
```

The container itself is named:

```text
task-postgres
```

---

# Docker Volume

PostgreSQL uses a named Docker volume:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

The volume stores PostgreSQL's database files outside the lifecycle of the PostgreSQL container.

This means that removing and recreating the container does not remove the database data.

The volume can be viewed using:

```cmd
docker volume ls
```

---

# Running the Application

## Prerequisites

Install:

- Docker Desktop
- Docker Compose

A separate PostgreSQL installation is not required because PostgreSQL runs inside Docker.

---

## Start the Complete Stack

From the project root directory:

```cmd
docker compose up -d --build
```

This command:

1. Builds the FastAPI Docker image.
2. Creates the Docker network.
3. Starts the PostgreSQL container.
4. Starts the FastAPI container.
5. Connects the application to PostgreSQL.

---

## Check Running Containers

Run:

```cmd
docker compose ps
```

Expected services:

```text
task-api
task-postgres
```

Both containers should show a running status.

---

# Access the API

The FastAPI application is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# Access PostgreSQL

PostgreSQL can be accessed directly from the running container using:

```cmd
docker exec -it task-postgres psql -U taskuser -d tasksdb
```

Once inside `psql`, view all tasks:

```sql
SELECT * FROM tasks;
```

View the table structure:

```sql
\d tasks
```

List all tables:

```sql
\dt
```

Exit PostgreSQL:

```sql
\q
```

---

# CRUD Testing

The CRUD endpoints were tested through Swagger UI.

## Create a Task

`POST /tasks`

Example request:

```json
{
    "title": "Learn Docker"
}
```

Example response:

```json
{
    "id": 1,
    "title": "Learn Docker",
    "done": false
}
```

---

## Get All Tasks

`GET /tasks`

Example response:

```json
[
    {
        "id": 1,
        "title": "Learn Docker",
        "done": false
    }
]
```

---

## Get a Task

`GET /tasks/{id}`

Example:

```text
GET /tasks/1
```

---

## Update a Task

`PUT /tasks/{id}`

Example request:

```json
{
    "title": "Learn Docker Compose",
    "done": true
}
```

---

## Delete a Task

`DELETE /tasks/{id}`

Example:

```text
DELETE /tasks/1
```

The endpoint returns:

```text
204 No Content
```

when the task is successfully deleted.

---

# Data Persistence Test

One of the main requirements of A3 was to demonstrate that PostgreSQL data survives container recreation.

The persistence test was performed as follows.

## Step 1 - Create Data

A task was created through the API.

Example:

```json
{
    "title": "Persistence Test"
}
```

---

## Step 2 - Verify the Data

The task was verified directly in PostgreSQL:

```sql
SELECT * FROM tasks;
```

---

## Step 3 - Remove the Containers

The application and database containers were removed using:

```cmd
docker compose down
```

This removes the containers and Docker network but keeps the named PostgreSQL volume.

---

## Step 4 - Start the Stack Again

The complete stack was started again:

```cmd
docker compose up -d
```

---

## Step 5 - Verify the Data Again

The PostgreSQL database was queried again:

```cmd
docker exec -it task-postgres psql -U taskuser -d tasksdb
```

Then:

```sql
SELECT * FROM tasks;
```

The previously created rows were still present.

Therefore, the database data successfully survived PostgreSQL container recreation.

---

# Persistence Architecture

```text
Before Restart

task-postgres
      |
      v
postgres_data
      |
      v
Tasks


docker compose down
      |
      v
task-postgres container removed
      |
      |
      └───────────────┐
                      │
              postgres_data
                  remains
                      │
                      ▼
              docker compose up
                      |
                      ▼
              New PostgreSQL
                  container
                      |
                      ▼
              Same task data
```

> **Important:** Do not use `docker compose down -v` when testing persistence. The `-v` option removes the named volume and therefore deletes the persisted database data.

---

# Docker Networking

The FastAPI and PostgreSQL services run in separate containers.

Inside the Docker Compose network:

```text
task-api
   |
   | db:5432
   v
task-postgres
```

The PostgreSQL service is reachable using the Compose service name:

```text
db
```

Therefore:

```text
postgresql://taskuser:taskpassword@db:5432/tasksdb
```

is used by the FastAPI container.

Using:

```text
localhost:5432
```

inside the FastAPI container would be incorrect because `localhost` refers to the FastAPI container itself.

---

# Application Architecture

## A1 - In-Memory Storage

```text
Client
   |
   v
FastAPI
   |
   v
Python List
```

Data was lost whenever the application restarted.

---

## A2 - SQLite

```text
Client
   |
   v
FastAPI
   |
   v
SQLite
   |
   v
tasks.db
```

The data became persistent using a local SQLite database.

---

## A3 - PostgreSQL + Docker

```text
Client
   |
   v
FastAPI
   |
   v
Repository Layer
   |
   v
PostgreSQL
   |
   v
Docker Volume
```

The final architecture provides:

- Database persistence
- Containerized PostgreSQL
- Repository-based database access
- Environment-based configuration
- Reproducible application setup using Docker Compose

---

# Stopping the Application

To stop and remove the containers while preserving the database volume:

```cmd
docker compose down
```

To start the application again:

```cmd
docker compose up -d
```

To rebuild the application after code changes:

```cmd
docker compose up -d --build
```

> Avoid `docker compose down -v` unless you intentionally want to delete the PostgreSQL volume and its data.

---

# Verification

The following checks were performed during A3:

- PostgreSQL 17 running successfully in Docker
- PostgreSQL `tasks` table created successfully
- FastAPI container successfully connected to PostgreSQL
- `DATABASE_URL` successfully configured through `.env`
- FastAPI CRUD operations tested through Swagger
- PostgreSQL data verified directly using `psql`
- Docker Compose successfully started both services
- PostgreSQL data remained available after `docker compose down` and `docker compose up`
- Persistent Docker volume verified

---

# A3 Summary

A2's SQLite storage was replaced with PostgreSQL running in Docker.

The final setup provides a reproducible two-container application stack:

```text
┌───────────────┐
│    FastAPI    │
│   task-api    │
└───────┬───────┘
        │
        │ DATABASE_URL
        │ db:5432
        ▼
┌───────────────┐
│  PostgreSQL   │
│ task-postgres │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ postgres_data │
│ Docker Volume │
└───────────────┘
```

The entire stack can be started with a single command:

```cmd
docker compose up -d --build
```

The database persists across container recreation through the Docker volume.