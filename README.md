# EventDesk

EventDesk is an event booking application with a FastAPI API and a React web interface. Organizers publish events, people reserve tickets, and administrators manage users and activity.

## Features

- Registration, sign in and sign out with hashed passwords, short lived JWT access tokens, and rotating refresh tokens.
- Database backed permissions for admins, organizers, and attendees; profile and account management.
- Draft, published, completed, and cancelled events with categories, tags, search, filters, and pagination.
- Ticket booking and cancellation with PostgreSQL row locks and a single transaction to prevent overselling. Event cancellation also cancels its active bookings.
- Ratings, reviews, and one level of replies; notifications; audit logs.
- Live ticket availability and notification updates through WebSockets.
- Scheduled event completion and email reminders through a systemd timer and Brevo.
- Soft deletion of users, events, bookings, reviews, and related catalog records.

## Stack and structure

Python 3.12, FastAPI, Pydantic, SQLAlchemy AsyncIO, PostgreSQL, Alembic, React 19, Vite, and pnpm.

```text
app/
  api/routes/       HTTP and WebSocket endpoints
  schemas/          Request and response validation
  services/         Business rules and transactions
  repositories/     Database queries
  models/           SQLAlchemy tables
  core/             Settings, authentication, permissions
  realtime/         WebSocket connections and publishing
  jobs/             Scheduled work
  integrations/     Brevo email client
alembic/            Database migrations
frontend/src/       React pages, components, and API client
```

A request generally follows **route → service → repository → PostgreSQL**. Services enforce permissions and business rules; repositories handle queries. The ERD is in [EventDesk ERD HD.svg](EventDesk%20ERD%20HD.svg).

## Run locally

Prerequisites: Python 3.12, `uv`, PostgreSQL, Node.js 20+, and pnpm. Run backend commands from the project root. The existing local PostgreSQL service on this machine uses port `55432`; on another machine, use your own PostgreSQL instance and set its host and port in `.env`.

1. Install Python dependencies and configure secrets:

   ```bash
   uv sync --frozen
   cp .env.example .env
   ```

   If `.env` already exists, keep it and do not overwrite it. Set `DATABASE_URL`, a random `SECRET_KEY` of at least 32 characters, the CORS origins, and the Brevo settings in `.env`. For a new database, create a PostgreSQL role and database first; use that role's password in `DATABASE_URL`. Never commit `.env`.

2. Start PostgreSQL and apply migrations:

   ```bash
   systemctl --user start eventdesk-postgres.service
   .venv/bin/alembic upgrade head
   .venv/bin/alembic check
   ```

   The `systemctl` command applies to this repository's local Linux setup. With a separately installed PostgreSQL server, start that server by its usual method instead. The database URL must point to the running server. A new checkout on another computer should also update the absolute paths in the supplied `.service` and `.timer` files before using them.

3. Start the API:

   ```bash
   .venv/bin/uvicorn app.main:app --reload
   ```

   Open [API docs](http://127.0.0.1:8000/docs). Keep this terminal running.

4. In a second terminal, start the frontend:

   ```bash
   cd frontend
   pnpm install --frozen-lockfile
   pnpm dev
   ```

   Open [EventDesk](http://127.0.0.1:5173). Vite forwards `/api` and `/ws` to the API at `127.0.0.1:8000`. Both servers must be running while using the site.

## Scheduled jobs and email

The `eventdesk-jobs.timer` runs every five minutes while its Linux user timer is active. It marks past events completed and sends due email reminders. The timer does not depend on the browser or API process, but it does depend on this computer being available. Start and inspect it with:

```bash
systemctl --user enable --now eventdesk-jobs.timer
systemctl --user list-timers eventdesk-jobs.timer
journalctl --user -u eventdesk-jobs.service -n 30 --no-pager
```

Set `BREVO_API_KEY` to a Brevo **API key**, and `BREVO_SENDER_EMAIL` to a verified sender. An SMTP key is for SMTP connections and is not accepted by the HTTP API used here. If Brevo rejects a reminder, the job logs the failure and leaves that reminder eligible for a later run.

## Verification

The repository does not currently include an automated test suite. These commands check imports, migration/model consistency, and the production frontend build:

```bash
.venv/bin/python -m compileall -q app alembic
.venv/bin/alembic check
cd frontend && pnpm build
```

For a manual smoke test, use the frontend or `/docs` to register, create and publish an event, book it from another account, cancel the event, and confirm the booking becomes cancelled. Check that admins can list events of every status, and that a user with a booking can still open a completed event to review it. New schema changes require an Alembic migration before running the API against that database.
