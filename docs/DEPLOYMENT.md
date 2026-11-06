# Free-tier deployment runbook

This runbook keeps the React frontend on GitHub Pages, PostgreSQL on Neon Free, and deploys the
FastAPI backend as a Vercel Hobby project. Following it creates no paid resource. The repository is
prepared for deployment, but no deployment is performed automatically.

## Cost and secret guardrails

- Select **Hobby** in Vercel and **Free** in Neon. Do not upgrade either project or add paid extras.
- Keep secrets only in Vercel environment variables. Never use `VITE_*` for a secret because Vite
  compiles those values into public browser JavaScript.
- Use Neon's **pooled** PostgreSQL connection string. Vercel instances use SQLAlchemy `NullPool` so
  they do not create a separate process-local connection pool.
- Scope production credentials to **Production**. For Preview deployments, use a separate Neon
  branch and separate credentials, or leave previews disabled; do not point untrusted preview code
  at the production database.

## 1. Prepare Neon Free

1. In the existing Neon Free project, open **Connect** and select the production database and role.
2. Enable **Pooled connection** and copy the resulting PostgreSQL URL. Keep all Neon TLS parameters.
3. Choose a Vercel function region close to the Neon region when creating the Vercel project.

The application accepts Neon's `postgresql://` URL and selects the installed psycopg 3 driver.

## 2. Import the API into Vercel

1. In Vercel, choose **Add New > Project** and import `p1y1m/space-mission-control`.
2. Select the **Hobby** plan.
3. Set **Root Directory** to `backend`.
4. Keep the detected **FastAPI** framework and default install/build settings. Do not override the
   build command: `[tool.vercel.scripts]` in `backend/pyproject.toml` runs migrations and bounded
   catalog seeding during the build.
5. Add these Production environment variables before the first deployment:

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | Neon pooled PostgreSQL URL (secret) |
   | `SECRET_KEY` | A new cryptographically random value of at least 32 bytes (secret) |
   | `CORS_ORIGINS` | `https://p1y1m.github.io` |
   | `COOKIE_SECURE` | `true` |
   | `ENVIRONMENT` | `production` |

Vercel supplies `VERCEL=1`; do not add it manually. The application deliberately rejects a Vercel
startup that falls back to SQLite, the development signing secret, or insecure cookies.

The serverless entrypoint remains `app.main:app`. Framework routing sends `/health`, `/docs`, and
all `/api/v1/*` paths to FastAPI without a catch-all rewrite. The build runs `alembic upgrade head`
before idempotently seeding the demonstration catalog; migrations do not run on cold starts.

## 3. Verify after the first deployment

Replace the placeholder with the Vercel-assigned hostname:

```bash
curl -fsS https://<vercel-project>.vercel.app/health
curl -fsS 'https://<vercel-project>.vercel.app/api/v1/satellites?page_size=1'
```

The health response must contain `"status":"ok"` and `"database":"connected"`. Check the first
build log for successful Alembic revisions without copying the database URL into logs or support
messages.

## 4. Connect GitHub Pages

After the Vercel hostname is final, create or update this public GitHub Actions repository variable:

```text
VITE_API_URL=https://<vercel-project>.vercel.app/api/v1
```

Re-run **Deploy Frontend to GitHub Pages**, then verify registration, login, refresh, satellite
catalog, watchlist, missions, CSRF-protected writes, logout, and a direct route refresh. This value is
a public URL, not a secret.

The API exposes `X-CSRF-Token` only to the configured CORS origin. This lets the separate GitHub
Pages site perform the existing double-submit CSRF check even though it cannot read Vercel's cookie
directly; the session token remains HttpOnly.

## Runtime limitations

- GitHub Pages and `vercel.app` are different sites. Cookies use `Secure; SameSite=None`, but a
  browser or privacy extension that blocks third-party cookies can still block authentication. Test
  the target browsers; a future same-site custom-domain design is the robust remedy.
- Authentication throttling is per Vercel instance, not globally distributed. It is a useful local
  guard, not a substitute for a shared edge/Redis rate limiter.
- Vercel's filesystem and instances are ephemeral. Durable application data belongs only in Neon.
- A failed migration stops the build. Review it, correct the migration or database configuration,
  and redeploy; do not bypass migrations or edit production schema manually.
