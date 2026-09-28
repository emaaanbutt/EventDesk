# EventDesk

EventDesk is an event booking app built with FastAPI, PostgreSQL, React, and Vite. Organizers publish events, users reserve tickets and write reviews, and admins manage users and activity. FastAPI serves the built React app and the API from one address.

## Features

- Registration and sign-in with hashed passwords, JWT access tokens, and rotating refresh tokens.
- Database-backed permissions for admins, organizers, and attendees.
- Events with drafts, publishing, categories, tags, search, filters, and pagination.
- Booking and cancellation with PostgreSQL row locks to prevent overselling.
- Reviews and one level of replies, notifications, audit logs, and live WebSocket updates.
- Scheduled event completion and email reminders through a systemd timer and Brevo.

## Project structure

```text
app/
  api/routes/      HTTP and WebSocket endpoints
  schemas/         Request and response validation
  services/        Business rules and transactions
  repositories/    Database queries
  models/          SQLAlchemy tables
  core/            Configuration, authentication, permissions
  db/              Engine and session setup
  realtime/        WebSocket rooms and publishers
  jobs/            Scheduled job entry point
  integrations/    Brevo email client
alembic/           Database migrations
frontend/src/      React pages, components, and API client
frontend/dist/     Generated frontend build (not committed)
```

The usual request flow is **React → FastAPI route → service → repository → PostgreSQL**. The [ERD](EventDesk%20ERD%20HD.svg) shows the database relationships.

## Run locally on this machine

You need Python 3.12, `uv`, Node.js 20+, `pnpm`, and PostgreSQL. Run backend commands from the repository root. The supplied user-level PostgreSQL service on this machine uses port `55432`.

1. Install dependencies if this is a fresh checkout:

   ```bash
   uv sync --frozen
   cd frontend
   pnpm install --frozen-lockfile
   cd ..
   ```

2. Keep your existing `.env`. For a new setup, copy `.env.example` to `.env` and fill in the PostgreSQL password, a random secret key of at least 32 characters, and the Brevo settings. Never commit `.env`.

3. Start PostgreSQL and apply migrations:

   ```bash
   systemctl --user start eventdesk-postgres.service
   .venv/bin/alembic upgrade head
   .venv/bin/alembic check
   ```

4. Build React, then start the **one** web server:

   ```bash
   cd frontend
   pnpm build
   cd ..
   .venv/bin/uvicorn app.main:app --reload
   ```

5. Open [EventDesk](http://127.0.0.1:8000/) and [API docs](http://127.0.0.1:8000/docs). FastAPI serves the generated `frontend/dist` files. You do not need a separate Vite server for this setup. Rebuild with `pnpm build` after changing frontend source. Restart Uvicorn if it was stopped; `--reload` watches Python code, not Vite source.

The API uses `/api` (for example, `POST /api/auth/login` and `GET /api/events/`). WebSockets use `/ws`. React pages and assets use `/` and `/assets`. The same origin is used for frontend and API, so CORS configuration is unnecessary.

### Optional frontend development server

For hot reloading while editing React, keep FastAPI running and start Vite in a second terminal:

```bash
cd frontend
pnpm dev
```

Open `http://127.0.0.1:5173`. Vite forwards `/api` and `/ws` to FastAPI on port `8000`. This is a development convenience; the one-server setup above uses the built frontend.

## Scheduled reminders

The systemd timer runs event completion and reminder emails every five minutes while this computer's user services are active. It does not require the browser or API server to stay open, but PostgreSQL, internet access, and this computer must be available. Brevo needs an API key and verified sender in `.env`.

```bash
systemctl --user enable --now eventdesk-jobs.timer
systemctl --user list-timers eventdesk-jobs.timer
journalctl --user -u eventdesk-jobs.service -n 30 --no-pager
```

The provided `.service` files contain absolute paths for this machine. Update those paths before installing them elsewhere.

## Checks

```bash
.venv/bin/python -m compileall -q app alembic
.venv/bin/alembic check
cd frontend && pnpm build
```

The repository does not currently have an automated test suite. For a manual check, register two users, create and publish an event, book it from the other account, cancel the booking, and confirm the ticket count and notifications update. Also test refreshing a React page directly at `/events/<event-id>`; FastAPI should return the React app and the page should load its data through `/api`.
