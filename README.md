# HelpDesk-MINI1

HelpDesk Mini — a Django + DRF backend (SQLite) providing a ticketing API with SLA timers, threaded comments, optimistic locking, idempotent create, per-user rate-limiting, timeline logging and a minimal single-file frontend for manual testing.

Quick start
1. Create a virtualenv and activate it.
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver

API (base: /api/)
- POST /api/auth/register {username,password,role}
- POST /api/auth/login {username,password} -> {token}
- POST /api/tickets (Idempotency-Key header) -> create ticket
- GET /api/tickets?limit=&offset=&q= -> {items, next_offset}
- GET /api/tickets/:id -> ticket
- PATCH /api/tickets/:id {version, assignee_id, status} -> optimistic locking
- POST /api/tickets/:id/comments (Idempotency-Key) {body,parent}

Health & meta
- GET /api/health
- GET /api/_meta
- /.well-known/hackathon.json

Test credentials
- admin / admin123 (created via seed script)

Notes
- Pagination: use `limit` and `offset`. Responses use the shape {items, next_offset}.
- Idempotency: include `Idempotency-Key` on POST requests to make creation idempotent.
- Rate limiting: middleware returns 429 with {"error":{"code":"RATE_LIMIT"}} when rate limit is exceeded.

Architecture (short)
Backend is Django + Django REST Framework with Token auth. Models include Ticket, Comment and TimelineEntry, and a Profile for roles (agent, user, admin). Key features implemented:
- Search across title/description/comments
- SLA deadline calculation on ticket create and a `breached` filter
- Optimistic locking using a `version` integer on Ticket (PATCH returns 409 on stale updates)
- Middleware for idempotency (dev cache) and per-minute rate limiting
- Minimal single-file frontend served from `static/app.js` with server-rendered fallbacks in `templates/`.

For deployment, move the idempotency and rate-limit cache to Redis or another shared cache and secure SECRET_KEY and database credentials via environment variables.

