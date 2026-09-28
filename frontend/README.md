# EventDesk frontend

A small React + Vite interface for the existing FastAPI API. It lives beside `app/` so the backend layers stay separate.

## Run locally

1. Start PostgreSQL and the backend from the repository root:

   ```bash
   systemctl --user start eventdesk-postgres.service
   .venv/bin/alembic upgrade head
   .venv/bin/uvicorn app.main:app --reload
   ```

2. In a second terminal, start the frontend:

   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

3. Open http://127.0.0.1:5173. The Vite development server forwards `/api/*` and `/ws/*` to FastAPI on `127.0.0.1:8000`. The backend must be running for data and sign-in to work.

Node.js 20+ and pnpm are required. This Codex workspace has a bundled Node runtime if `node` is not on your shell's `PATH`:

```bash
export PATH="/home/wamolabs/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH"
/home/wamolabs/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm install
/home/wamolabs/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm dev
```

## Pages

- Public: home, published event list with filters, event details, reviews, sign in, and registration.
- Signed in: profile/password, bookings, notifications, and review actions.
- Organizer: own events, event creation and editing, publishing and cancellation, and replies to reviews on owned events.
- Admin: user roles/status, category and tag creation, audit logs, and event lookup by ID.

The backend remains the authority for every permission check. The UI hides actions that do not fit a role, but an API request is still checked by FastAPI.

Access and refresh tokens are stored in this browser's local storage. `src/lib/api.js` adds the access token to protected calls and rotates the token pair through `/auth/refresh` after a 401. Signing out revokes the refresh token through `/auth/logout` and clears local storage. Event availability and notifications use the backend WebSocket routes.

The backend currently has no endpoint for listing every draft event or loading a cancelled event publicly. Admins can open a known event ID from the admin page. A cancelled event may still be referenced by a booking or notification even though its public detail page returns 404.
