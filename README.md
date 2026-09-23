# EventDesk

EventDesk is a FastAPI-based backend for an event management platform. The project currently focuses on the auth, user management, and role-based access flow.

This is a layered app:
- Routes accept HTTP requests
- Services handle business logic
- Repositories talk to the database
- Models define the database structure
- Dependencies verify tokens and user identity

---

## What this project does

The current version includes:
- User registration
- Login and logout
- Refresh token flow
- JWT-based access control
- User profile update
- Password change
- Admin-only user listing, role updates, activation toggles, and soft delete
- Health checks for the API and database
- PostgreSQL async connection using SQLAlchemy

This is a solid backend foundation for the EventDesk platform, and the auth + user system is the main completed part so far.

---

## Request flow: where a request starts and ends

A normal request moves like this:

1. The client sends an HTTP request to the API.
2. FastAPI loads the app from [app/main.py](app/main.py).
3. The request matches a router in one of the route files under [app/api/routes](app/api/routes).
4. The route calls a service in [app/services](app/services).
5. The service applies the business logic, validation, and access checks.
6. The service calls a repository in [app/repositories](app/repositories) to read or write data.
7. The repository uses SQLAlchemy models in [app/models](app/models) to interact with PostgreSQL.
8. The response is returned back to the client.

Example:
- POST /auth/login
- route: [app/api/routes/auth.py](app/api/routes/auth.py)
- service: [app/services/auth_service.py](app/services/auth_service.py)
- repository: [app/repositories/user_repository.py](app/repositories/user_repository.py) and [app/repositories/refresh_token_repository.py](app/repositories/refresh_token_repository.py)
- database: PostgreSQL via [app/db/session.py](app/db/session.py)

---

## Auth flow in simple words

### 1) Register
Client sends:
- name
- email
- password
- role

The request hits the register route in [app/api/routes/auth.py](app/api/routes/auth.py). The service checks whether the email already exists, creates the user, and issues a fresh access + refresh token pair.

### 2) Login
Client sends email + password.

The app:
- finds the user by email
- verifies the password hash
- checks if the account is active
- issues a new token pair

### 3) Access token usage
The access token is used for protected routes.

The token is read in [app/core/dependencies.py](app/core/dependencies.py), where the app:
- extracts the bearer token
- validates the JWT
- loads the user from the database
- rejects invalid, deleted, or inactive users

This is how the app knows who is making the request.

### 4) Refresh token flow
When the access token expires, the client sends the refresh token to POST /auth/refresh.

The system:
- validates the refresh token type
- loads the user
- checks that the token is still stored and not revoked/expired
- issues a new access + refresh token pair
- invalidates the old refresh token after rotation

### 5) Logout
Client sends the latest refresh token to POST /auth/logout.

The app marks that refresh token as revoked, so it can no longer be used.

---

## Folder layout and how they connect

### [app/main.py](app/main.py)
This is the entry file for FastAPI. It pulls in the routers and exposes the app object.

### [app/api/routes](app/api/routes)
This folder contains API endpoints.
- [app/api/routes/auth.py](app/api/routes/auth.py): register, login, refresh, logout, me
- [app/api/routes/users.py](app/api/routes/users.py): profile and admin user actions
- [app/api/routes/health.py](app/api/routes/health.py): health endpoints

### [app/services](app/services)
This is where business logic lives.
- [app/services/auth_service.py](app/services/auth_service.py): auth logic
- [app/services/user_service.py](app/services/user_service.py): profile and admin user rules
- [app/services/authorization_service.py](app/services/authorization_service.py): permission checks

### [app/repositories](app/repositories)
Repositories handle database queries.
- [app/repositories/user_repository.py](app/repositories/user_repository.py): user lookups and updates
- [app/repositories/refresh_token_repository.py](app/repositories/refresh_token_repository.py): refresh token storage and rotation

### [app/models](app/models)
This is the database model layer.
- [app/models/users.py](app/models/users.py): user table
- [app/models/refresh_tokens.py](app/models/refresh_tokens.py): refresh tokens
- [app/models/events.py](app/models/events.py), [app/models/bookings.py](app/models/bookings.py), etc.: domain models for the broader event platform

### [app/core](app/core)
Core infrastructure for the app.
- [app/core/config.py](app/core/config.py): settings and environment loading
- [app/core/security.py](app/core/security.py): password hashing and JWT creation/validation
- [app/core/dependencies.py](app/core/dependencies.py): auth and DB dependencies for routes
- [app/core/role_policy.py](app/core/role_policy.py): role-based permission rules

### [app/db](app/db)
Database setup and async engine config.
- [app/db/session.py](app/db/session.py): SQLAlchemy async engine and session maker
- [app/db/base.py](app/db/base.py): base model + timestamp mixin

### [app/schemas](app/schemas)
Input/output validation types.
- [app/schemas/user.py](app/schemas/user.py): user-related request and response models
- [app/schemas/auth.py](app/schemas/auth.py): token and auth payload schemas

---

## Local setup

From the project root:

```bash
uv sync --frozen
```

The local PostgreSQL cluster is stored in `.local-postgres/data`. Start it if it is stopped:

```bash
/usr/lib/postgresql/16/bin/pg_ctl -D .local-postgres/data -l .local-postgres/server.log -o '-h 127.0.0.1 -p 55432 -k /tmp' start
```

The local [.env](.env) already has a working connection. For another machine, copy `.env.example` to `.env` and set the actual database password and a secret key of at least 32 characters.

Example:

```env
DATABASE_URL=postgresql+asyncpg://eventdesk:YOUR_DATABASE_PASSWORD@127.0.0.1:55432/eventdesk_auth
SECRET_KEY=REPLACE_WITH_AT_LEAST_32_RANDOM_CHARACTERS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Apply the auth migration, then start the app:

```bash
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

Public registration creates organizers or attendees. To create the first admin, run this command from the project root; it prompts for the admin password:

```bash
.venv/bin/python -m app.scripts.create_admin --email admin@example.com --name "Admin Name"
```

After one active admin exists, use the admin role-change endpoint to promote other users.

Open the docs here:
- http://127.0.0.1:8000/docs

---

## Completed work

The following is done and working in the project structure:
- Async FastAPI app setup
- SQLAlchemy + PostgreSQL async engine
- UUID-based user identifiers
- User model with role support
- Password hashing with bcrypt
- JWT access and refresh token flow
- Refresh token rotation and revocation
- Auth dependency for bearer token validation
- User profile and account management routes
- Role-based authorization checks
- Health endpoints for API and database
- Clean service/repository separation

---

## Still in progress / next layer

The event platform is not fully finished yet. The next likely work items are:
- event CRUD
- booking flow
- review system
- notification system
- more advanced permission model tied to real database policies
- migration cleanup and schema verification across all models

The auth and user foundation is already in place and is the most complete part of the project right now.
