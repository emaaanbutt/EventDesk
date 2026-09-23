# EventDesk auth branch

This branch exposes only the existing auth, health, and root routes. PostgreSQL uses a local cluster under `.local-postgres/data`; its data and `.env` are ignored by Git.

## Start

From the `EventDesk` directory:

```bash
/usr/lib/postgresql/16/bin/pg_ctl -D .local-postgres/data -l .local-postgres/server.log -o '-h 127.0.0.1 -p 55432 -k /tmp' start
uv sync --frozen
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

The first command is only needed when PostgreSQL is stopped. `.env` already contains the working connection URL and JWT secret. Open `http://127.0.0.1:8000/docs` for the request forms. Check `GET /health/db` for the database connection.

Register with `POST /auth/register` using `name`, `email`, `password`, and an explicit `role` (`organizer` or `attendee`). A password needs at least 8 characters, an uppercase letter, a digit, and a special character. Public registration cannot create an admin.

`POST /auth/login` accepts email and password. Put the returned access token in the `Authorization: Bearer <token>` header for `GET /auth/me`. Send the refresh token in JSON to `POST /auth/refresh` to receive a new pair. The old refresh token is then invalid. Send the latest refresh token to `POST /auth/logout` to revoke it. The access token remains valid until its 30 minute expiry; refresh tokens expire after 7 days.

## File flow

`app/main.py` mounts the routes. `app/api/routes/auth.py` accepts and validates HTTP input, then calls `app/services/auth_service.py`. The service checks credentials and handles token issuance and rotation. `app/repositories/user_repository.py` and `app/repositories/refresh_token_repository.py` perform database queries. `app/models/users.py` and `app/models/refresh_tokens.py` define the two auth tables. `app/core/security.py` hashes passwords and signs/verifies JWTs. `app/core/dependencies.py` reads the bearer token and reloads the current user for protected requests. `app/db/session.py` creates database sessions; `app/core/config.py` reads `.env`. Alembic's migration creates only the two auth tables.
