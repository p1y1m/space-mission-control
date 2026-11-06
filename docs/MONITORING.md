# Operations and monitoring

The API exposes `GET /health`, returning only service state, database connectivity, and an
UTC timestamp. It intentionally excludes connection strings, versions, credentials, and host
details. Vercel or an external uptime monitor should probe this endpoint. A `degraded` response
means the function is alive but PostgreSQL is unavailable.

Application requests are written as JSON logs with method, path, response status, and duration.
In production, review Vercel runtime logs or route logs to an approved monitor and alert on:

- health checks failing for five minutes;
- sustained 5xx responses above 2%;
- p95 request duration above one second;
- PostgreSQL connection exhaustion or storage thresholds;
- authentication throttling spikes.

The browser shows loading, empty, API failure, and error-boundary states. No telemetry, secrets,
or personally identifying account details are written to structured request logs.

## Incident baseline

1. Confirm `/health` and the Vercel deployment state.
2. Check database availability in Neon without exposing its URL.
3. Review the latest migration and structured application errors.
4. Roll back the Vercel deploy if the previous revision is healthy.
5. Rotate `SECRET_KEY` only with the understanding that all active sessions will be invalidated.

For production, add an external uptime probe, error tracking, database backups, and tested restore
procedures. The repository does not claim those managed services are already configured.
