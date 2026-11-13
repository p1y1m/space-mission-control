# Space Mission Control

# Author: Pedro Yanez Melendez

An aerospace-inspired satellite tracking and simulated mission-operations platform. The project
combines a responsive React operations console with a security-focused FastAPI service, relational
PostgreSQL data, automated tests, containers, and low-cost deployment preparation.

> **Data integrity:** catalog identities use real NORAD identifiers. Bundled map coordinates are
> clearly marked **demo propagated estimates** and are not spacecraft telemetry. This application
> cannot command spacecraft.

## Product capabilities

- Mission-control dashboard with an OpenStreetMap/Leaflet tracking matrix, selected-asset panel,
  catalog statistics, data-quality status, charts, and activity context.
- Searchable, filterable, sorted, and paginated satellite catalog with individual asset dossiers.
- Account registration, login/logout, Argon2 password hashing, HttpOnly sessions, CSRF protection,
  strict validation, and authenticated route handling.
- Private watchlist CRUD with per-asset notes and notification preferences.
- Private mission CRUD with status, priority, descriptions, and many-to-many satellite assignment.
- User-scoped analytics for mission state and watchlist composition.
- API/database health checks, structured JSON logs, loading and empty states, and an error boundary.
- Responsive premium dark UI for desktop, tablet, and mobile with keyboard-friendly controls.

## Screenshots

The interface is implemented and can be captured after startup with Playwright:

```bash
cd frontend
npx playwright screenshot --device="Desktop Chrome" http://localhost:5173 docs/dashboard.png
```

Suggested portfolio captures: login, orbital dashboard, satellite explorer, and mission portfolio.
Screenshots are intentionally not committed until generated from a running local deployment.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query |
| Geospatial / charts | React Leaflet, OpenStreetMap, Recharts |
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic |
| Security | Argon2, signed JWT session cookies, double-submit CSRF, CORS controls |
| Database | PostgreSQL 16 locally; Neon-compatible in production |
| Quality | Pytest, Vitest, React Testing Library, Playwright, ESLint |
| Delivery | Docker Compose, GitHub Actions, GitHub Pages, Vercel Functions |

## Architecture

```mermaid
flowchart LR
    U[Operator browser] -->|HTTPS static assets| GH[GitHub Pages\nReact + Vite]
    GH -->|REST + credentials + CSRF| API[Vercel Hobby\nFastAPI function]
    API -->|SQLAlchemy / TLS| DB[(Neon PostgreSQL)]
    API -. optional refresh .-> CT[CelesTrak public catalog]
    API --> LOG[Structured logs / health probe]
    subgraph Local development
      FE[Frontend container] --> BE[Backend container]
      BE --> PG[(PostgreSQL container)]
    end
```

The frontend owns presentation and server-state caching. FastAPI is the authorization boundary.
User ownership is enforced inside database queries, not trusted to browser routes. PostgreSQL holds
users, catalog assets, watchlist entries, missions, many-to-many assignments, and position-sample
schema support.

## Quick start with Docker

Requirements: Docker Engine with Compose v2.

```bash
cp .env.example .env
# Set SECRET_KEY and POSTGRES_PASSWORD in .env
docker compose up --build
```

Open:

- Frontend: <http://localhost:5173>
- Frontend on standard HTTP: <http://localhost>
- OpenAPI: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

Common commands:

```bash
docker compose down                         # stop containers, keep database
docker compose logs -f                      # follow service logs
docker compose exec backend alembic upgrade head
docker compose run --rm backend pytest -q
docker compose run --rm frontend npm test -- --run
docker compose run --rm frontend npm run build
docker compose down -v                      # intentional local DB reset only
```

The `Makefile` provides equivalent `make up`, `make down`, `make migrate`, `make test`, and
`make reset` shortcuts. `make reset` explicitly reports that it removes this project's volume.

## Native development

Backend:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://mission_control:password@localhost/mission_control'
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (Node 22 recommended):

```bash
cd frontend
npm ci
printf 'VITE_API_URL=http://localhost:8000/api/v1\n' > .env.local
npm run dev
```

## Configuration

| Variable | Used by | Purpose |
|---|---|---|
| `DATABASE_URL` | API | SQLAlchemy PostgreSQL URL (`postgresql+psycopg://...`) |
| `SECRET_KEY` | API | Random signing secret, at least 32 random bytes recommended |
| `CORS_ORIGINS` | API | Comma-separated exact browser origins |
| `COOKIE_SECURE` | API | `true` for cross-site HTTPS production cookies |
| `VITE_API_URL` | Browser | Public API base, ending in `/api/v1` |
| `VITE_PROXY_TARGET` | Vite dev server | Internal API origin used only by local Docker development |

Do not expose server secrets through `VITE_*`; those values are compiled into public JavaScript.

## Data and migrations

The Alembic revisions create the relational model, constraints, ownership foreign keys, indexes,
cascade rules, mission join table, and orbital-element cache. The API seeds a small bounded catalog
on an empty database. It does not fetch an enormous orbital catalog during startup or make
availability depend on a third party.

The bundled catalog is an explicit offline/demo mode. An opt-in sync makes one grouped CelesTrak
request, caches new TLE snapshots, propagates matched assets with SGP4, and stores an application
position sample. It never labels propagation as telemetry:

```bash
docker compose exec backend python -m app.sync_celestrak
```

The grouped source currently targets CelesTrak's `stations` catalog to keep the request bounded;
only matching assets in the local catalog are updated. Schedule this command conservatively in a
production job and continue to honor provider attribution and rate limits.

Create and apply future migrations with:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
docker compose exec backend alembic upgrade head
```

## Tests

```bash
# Backend unit/integration tests (SQLite fallback locally; PostgreSQL in CI)
docker compose run --rm backend pytest --cov=app --cov-report=term-missing

# Frontend component tests, type check, and production build
docker compose run --rm frontend npm test -- --run
docker compose run --rm frontend npm run build

# Critical browser workflow; all three app containers must be running
cd frontend && npx playwright install chromium && npm run e2e
```

Backend tests cover health, registration/login failure, protected routes, catalog filtering,
watchlist CRUD, mission CRUD, validation, CSRF, and cross-user isolation. The browser flow covers
registration, catalog browsing, watchlist creation, mission creation, and core navigation.

## API surface

| Area | Endpoints |
|---|---|
| Health | `GET /health` |
| Authentication | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| Satellites | `GET /satellites`, `GET /satellites/{id}` |
| Watchlist | `GET/POST /watchlist`, `PATCH/DELETE /watchlist/{id}` |
| Missions | `GET/POST /missions`, `PATCH/DELETE /missions/{id}` |
| Analytics | `GET /analytics` |

Interactive schemas and exact response models are available at `/docs` and `/openapi.json`.
The API root (`GET /`) returns a small JSON deployment marker so a frontend deployment cannot be
mistaken for the FastAPI service.

## Deployment

For the exact free-tier procedure and cost guardrails, see the
[deployment runbook](docs/DEPLOYMENT.md).

### Backend and database

1. Create a Neon PostgreSQL project and copy its pooled TLS URL.
2. Import this repository into Vercel Hobby with `backend` as the project Root Directory.
3. Configure the Neon pooled `DATABASE_URL`, a random `SECRET_KEY`, the exact CORS origin, and secure cookies.
4. Vercel's build hook applies `alembic upgrade head`; serverless cold starts never run migrations.

### Frontend

1. In GitHub repository variables, set `VITE_API_URL=https://<vercel-host>/api/v1`.
2. Enable GitHub Pages with **GitHub Actions** as the source.
3. Run the “Deploy Frontend to GitHub Pages” workflow.
4. Update `vite.config.ts` if the repository name is not `space-mission-control`.

The workflow builds a `404.html` SPA fallback for deep-link refreshes. No cloud resources are
created and no deployment credentials are stored in this repository.

## Security and monitoring

See [security guidance](docs/SECURITY.md) and [monitoring/runbook](docs/MONITORING.md). The important
production limitations are the per-instance authentication rate limiter, no managed alerting in the
repository, and cookie behavior that must be verified against the final GitHub Pages/Vercel domains.

## Engineering competencies demonstrated

- Responsive component architecture, routing, stateful forms, accessible interactions, mapping,
  charting, and server-state cache invalidation.
- REST design, schema validation, ORM relationships, migrations, transactions, error semantics,
  pagination, structured logs, and health probes.
- Authentication, password security, cookies, CSRF, CORS, ownership checks, data isolation, and
  defensive configuration.
- Unit, integration, component, and browser test layers with PostgreSQL-backed CI.
- Container orchestration, environment separation, CI quality gates, static frontend hosting, and
  serverless API/database deployment design.

## Trade-offs and future work

- Add scheduled, cached CelesTrak OMM/TLE ingestion and SGP4 propagation with historical samples.
- Replace the in-process rate limiter with a distributed edge or Redis-backed limit.
- Add email/push delivery behind the stored watchlist preference; no fake notifications are sent.
- Add account password change/deletion, audit events, CSP reporting, and managed error tracking.
- Add broader frontend interaction tests and visual regression baselines.
- Parameterize the GitHub Pages base path from repository metadata for forks.

This is a portfolio-grade mission-planning simulation, not a certified flight system.
