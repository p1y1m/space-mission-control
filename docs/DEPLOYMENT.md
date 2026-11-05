# Free-tier deployment runbook

This runbook deploys the existing frontend on GitHub Pages, PostgreSQL on Neon, and the FastAPI
container on Render. It intentionally creates no Render database, persistent disk, worker, or paid
compute resource.

## Cost guardrails

- Keep the Neon project on **Free**.
- Keep the Render workspace on **Hobby** and the web service on the **Free** instance type.
- Do not add a Render database, disk, background worker, workflow, or custom domain.
- To guarantee that Render cannot create usage charges, do not attach a payment method. Without one,
  Render suspends free services or builds after included usage is exhausted instead of charging.
- Before confirming the Render Blueprint, verify that its summary shows one web service with
  `plan: free` and no other resources.

## 1. Create the Neon database

1. Sign in to Neon and create a project named `space-mission-control` on the **Free** plan.
2. Choose a region near the Render service region to reduce latency.
3. Keep the default database and role, and copy the pooled PostgreSQL connection string.
4. Store the connection string only in Render's `DATABASE_URL` secret field. Never commit it, put it
   in a GitHub Actions variable, or paste it into chat or logs.

The application accepts Neon's standard `postgresql://` URL and automatically selects the installed
psycopg 3 driver. TLS query parameters supplied by Neon are preserved.

## 2. Create the Render API

1. Sign in to Render and connect the GitHub repository `p1y1m/space-mission-control`.
2. Choose **New > Blueprint**, select the repository, and use the root `render.yaml`.
3. Verify the preview contains only `space-mission-control-api`, with instance type **Free**.
4. Enter the Neon connection string for the prompted `DATABASE_URL` value.
5. Confirm the Blueprint. Render generates `SECRET_KEY`; the repository supplies these non-secret
   values:
   - `CORS_ORIGINS=https://p1y1m.github.io`
   - `COOKIE_SECURE=true`
   - `ENVIRONMENT=production`

The container runs `alembic upgrade head` before starting Uvicorn, because Render pre-deploy commands
are not available on Free web services. Startup also seeds the bounded demonstration catalog when the
database is empty.

## 3. Verify the API

After Render provides the service URL, verify:

```bash
curl -fsS https://<render-service>.onrender.com/health
curl -fsS https://<render-service>.onrender.com/api/v1/satellites?page_size=1
```

The health response must report `"status":"ok"` and `"database":"connected"`. The first request
after 15 minutes of inactivity can take about a minute while a Free web service wakes up.

## 4. Connect GitHub Pages to the API

Create the public repository Actions variable below (it contains only a public API URL, never a
secret):

```text
VITE_API_URL=https://<render-service>.onrender.com/api/v1
```

Then manually run **Deploy Frontend to GitHub Pages**. Confirm registration, login, satellite
catalog, watchlist, missions, logout, and a direct `/space-mission-control/login` refresh.

## Rollback and operations

- Render deploys only after GitHub checks pass.
- Database migrations are versioned in `backend/alembic/versions` and run on each container start.
- Neon is the durable datastore; Render's local filesystem is ephemeral and stores no application
  data.
- Free Render services sleep after inactivity, and their first request after sleeping is expected to
  be slow.
