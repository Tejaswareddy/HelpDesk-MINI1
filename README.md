HelpDesk Mini
===============

Run: create virtualenv, pip install -r requirements.txt, then run migrations and startserver.

APIs:
- POST /api/auth/register {username,password,role}
- POST /api/auth/login {username,password} -> {token}
- POST /api/tickets (Idempotency-Key header) -> create ticket
- GET /api/tickets?limit=&offset=&q= -> {items, next_offset}
- GET /api/tickets/:id -> ticket
- PATCH /api/tickets/:id {version, assignee_id, status} -> optimistic locking
- POST /api/tickets/:id/comments (Idempotency-Key) {body,parent}

Health & meta:
- GET /api/health
- GET /api/_meta
- /.well-known/hackathon.json

Test credentials:
- admin / password (created via seed)

Pagination: use limit and offset. Response: {items, next_offset}
Idempotency: include header Idempotency-Key
Rate limit: 60 req/min per user -> 429 {"error":{"code":"RATE_LIMIT"}}

Architecture (120 words):
Backend is Django + DRF with Token auth. Models include Ticket, Comment, TimelineEntry and Profile for roles. API views implement listing with search (title, description, comments), ticket creation with SLA deadline calculation, optimistic locking via a version integer for PATCH operations, and timeline entries for actions. Middleware provides an in-memory idempotency cache and per-minute rate-limiting. Frontend is a minimal React-ready template served by Django; for the hackathon you can extend it into full React SPA that talks to the API. SQLite keeps data local and simple for testing and judge evaluation.
