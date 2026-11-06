# Security model

- Passwords are hashed with Argon2 through `pwdlib`; password hashes are never serialized.
- Authentication uses signed, expiring JWTs in HttpOnly cookies. Production cookies use
  `Secure; SameSite=None` for the separate GitHub Pages and Vercel origins.
- State-changing authenticated requests require a double-submit CSRF token. The API exposes that
  token in an allowed response header for the separate GitHub Pages origin; the session cookie
  remains HttpOnly and CORS prevents unapproved origins from reading the header.
- Every watchlist and mission query is scoped by the authenticated user's database ID.
- SQLAlchemy parameterizes queries and Pydantic constrains request size and shape.
- CORS is credential-aware and accepts only configured origins.
- Authentication attempts have a lightweight per-process rate limit. A distributed production
  deployment should replace this with a shared Redis or edge rate limiter.
- Responses set nosniff, frame-denial, and strict-referrer headers. Vercel or an edge proxy should
  add HSTS and a carefully tested Content Security Policy.

Use a random 32+ byte `SECRET_KEY`, exact HTTPS origins, Neon TLS, dependency scanning, regular
backups, and secret rotation in production. Never put secrets in `VITE_*` variables: Vite values
are public browser configuration.
