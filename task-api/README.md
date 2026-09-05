# FlyRank Backend Internship

A FastAPI backend developed progressively through the FlyRank Backend Internship assignments.

## Assignments

- A1 — FastAPI Task CRUD API
- A2 — SQLite persistence
- A3 — PostgreSQL + Docker Compose
- A4 — Supabase Authentication

---

# A4 — Authentication

## Overview

A4 adds authentication and authorization to the Task API using Supabase Auth.

The API now supports:

- User signup
- User login
- User logout
- Supabase JWT verification
- Protected API routes
- Reusable authentication dependency
- Swagger Bearer authentication

---

## Tech Stack

- Python
- FastAPI
- Supabase Auth
- PostgreSQL
- Psycopg
- Docker / Docker Compose
- Pydantic
- python-dotenv
- Swagger / OpenAPI

---

## Project Structure

```text
flyrank-backend/
│
├── task-api/
│   ├── main.py
│   ├── auth.py
│   ├── supabase_client.py
│   ├── database.py
│   ├── postgres_repository.py
│   ├── repository.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── schema.sql
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=your_password
POSTGRES_DB=tasksdb
DATABASE_URL=postgresql://taskuser:your_password@db:5432/tasksdb

SUPABASE_URL=your_project_url
SUPABASE_KEY=your_publishable_or_anon_key

PORT=8000
```

The `.env` file contains sensitive configuration and is ignored by Git.

Do not commit `.env`, passwords, Supabase credentials, or access tokens.

Use `.env.example` as the safe configuration template.

---

## Supabase Authentication Setup

A4 uses Supabase Auth for user authentication and JWT verification.

### Setup

1. Create a project in Supabase.
2. Open the project's API settings.
3. Copy the Project URL.
4. Copy the Publishable key (or legacy `anon` key if applicable).
5. Add both values to `.env`.

Example:

```env
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_publishable_or_anon_key
```

The Supabase secret/service-role key is not used by this application.

For local testing, email confirmation was disabled in Supabase Auth so newly created test users could log in immediately.

---

## Running the Application

### Local Development

Activate the virtual environment:

```cmd
venv\Scripts\activate
```

Move into the API directory:

```cmd
cd task-api
```

Start the FastAPI server:

```cmd
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Docker + PostgreSQL

The application can also be started together with PostgreSQL using Docker Compose.

From the project root:

```cmd
docker compose up -d
```

Stop the services with:

```cmd
docker compose down
```

PostgreSQL data is stored in the Docker named volume `postgres_data`, allowing database data to persist when containers are recreated.

---

# A4 Authentication Flow

The authentication flow uses Supabase Auth and Bearer JWTs.

```text
User
 │
 ├── POST /auth/signup
 │          ↓
 │    Supabase Auth
 │
 ├── POST /auth/login
 │          ↓
 │    Access Token + Refresh Token
 │
 └── Protected Request
            ↓
    Authorization: Bearer <JWT>
            ↓
      get_current_user()
            ↓
    Supabase JWT verification
            ↓
       Authenticated User
            ↓
       Protected Route
```

---

## Signup

```http
POST /auth/signup
```

Creates a new user account using Supabase Auth.

Request:

```json
{
  "email": "test@example.com",
  "password": "your-password"
}
```

Successful signup returns HTTP `201`.

---

## Login

```http
POST /auth/login
```

Authenticates an existing user.

Request:

```json
{
  "email": "test@example.com",
  "password": "your-password"
}
```

A successful login returns an access token and refresh token.

Example response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

The access token is a Supabase JWT and must be kept private.

---

## Protected Routes

Protected endpoints require a valid Bearer access token.

The request must contain:

```http
Authorization: Bearer <access_token>
```

Authentication is implemented through the reusable `get_current_user()` dependency in `auth.py`.

The dependency:

1. Extracts the Bearer token.
2. Sends the token to Supabase Auth.
3. Verifies the token.
4. Retrieves the authenticated user.
5. Rejects missing, invalid, or expired tokens with HTTP `401`.

---

## Reusable Authentication Dependency

The authentication logic is centralized in:

```text
task-api/auth.py
```

Protected routes use:

```python
user=Depends(get_current_user)
```

This avoids duplicating JWT verification code in every protected endpoint.

The same dependency is used by:

- `/protected/profile`
- `/protected/dashboard`
- `/auth/logout`

---

# API Routes

| Method | Endpoint | Authentication |
|---|---|---|
| GET | `/` | Public |
| GET | `/health` | Public |
| GET | `/tasks` | Public |
| GET | `/tasks/{id}` | Public |
| POST | `/tasks` | Public |
| PUT | `/tasks/{id}` | Public |
| DELETE | `/tasks/{id}` | Public |
| POST | `/auth/signup` | Public |
| POST | `/auth/login` | Public |
| POST | `/auth/logout` | Protected |
| GET | `/public/info` | Public |
| GET | `/protected/profile` | Protected |
| GET | `/protected/dashboard` | Protected |

---

# Protected Profile

```http
GET /protected/profile
```

Requires a valid Supabase access token.

The endpoint uses the reusable `get_current_user()` dependency and returns information about the authenticated user.

Example response:

```json
{
  "id": "user-id",
  "email": "user@example.com",
  "created_at": "..."
}
```

---

# Protected Dashboard

```http
GET /protected/dashboard
```

This endpoint demonstrates that the same authentication dependency can be reused by multiple protected routes.

It does not contain separate JWT verification logic.

Example response:

```json
{
  "message": "Welcome to your dashboard.",
  "user_id": "user-id"
}
```

---

# Logout

```http
POST /auth/logout
```

Logout is itself a protected endpoint.

The request must contain a valid Bearer access token.

After the authentication dependency verifies the user, the endpoint calls:

```python
supabase.auth.sign_out()
```

A successful logout returns:

```text
204 No Content
```

---

# Swagger Authentication

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI's `HTTPBearer` security scheme is used to define Bearer authentication.

Protected endpoints display a lock icon in Swagger UI.

Click the **Authorize** button and provide the access token.

Swagger then sends the token using:

```http
Authorization: Bearer <access_token>
```

This allows protected endpoints to be tested directly from Swagger.

---

## Authentication Testing

The following authentication cases were tested:

| Test | Expected Status |
|---|---:|
| Signup with valid data | `201` |
| Login with valid credentials | `200` |
| Protected route without token | `401` |
| Protected route with valid JWT | `200` |
| Protected route with tampered JWT | `401` |
| Logout with valid JWT | `204` |

---

# Error Handling

| Situation | Status Code |
|---|---:|
| Successful signup | `201` |
| Successful login | `200` |
| Missing access token | `401` |
| Invalid or expired JWT | `401` |
| Invalid login credentials | `401` |
| Invalid signup request | `400` |
| Successful logout | `204` |

---

# Security

- Supabase configuration is loaded from environment variables.
- `.env` is excluded from Git.
- No Supabase secret/service-role key is used.
- JWTs are verified through Supabase Auth.
- Protected routes use a reusable authentication dependency.
- Access tokens must not be committed to the repository.
- Database passwords and other secrets must not be committed to the repository.

---

# A3 — PostgreSQL + Docker Compose

A3 migrated the Task API from SQLite to PostgreSQL.

PostgreSQL runs inside Docker using Docker Compose.

The application connects to PostgreSQL through:

```text
DATABASE_URL
```

The database schema is initialized using:

```text
schema.sql
```

The repository layer separates database operations from FastAPI routes.

---

# A2 — SQLite Persistence

A2 migrated the original in-memory task storage to SQLite.

The SQLite database was used for persistent task storage and CRUD operations.

This implementation was later replaced by PostgreSQL during A3.

---

# A1 — FastAPI CRUD API

A1 implemented the initial Task CRUD API using FastAPI.

The API supported:

- Create task
- Read all tasks
- Read task by ID
- Update task
- Delete task

The initial implementation stored tasks in memory.

---

# Testing

The API was tested using:

- FastAPI Swagger UI
- Supabase authentication
- Valid and invalid JWTs
- Protected and public routes
- PostgreSQL persistence
- Docker Compose

Authentication verification included:

```text
Valid JWT       → 200
Tampered JWT    → 401
No JWT          → 401
```

---

# Project Status

A1, A2, A3, and A4 have been implemented progressively.

A4 completes the authentication layer by adding:

- Supabase Auth
- Signup
- Login
- Logout
- JWT verification
- Reusable authentication dependency
- Multiple protected routes
- Swagger Bearer authentication
