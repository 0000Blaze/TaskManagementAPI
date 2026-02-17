# MediVue Backend Assessment — Task Management API

This repository implements the **Task Management API** described in the assessment brief.

## Quickstart (Docker + PostgreSQL)

Prereqs: Docker Desktop

```bash
docker compose up --build
```

API will be available at:
- http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Environment Variables

- `DATABASE_URL` (required in non-test runs)
  - Example: `postgresql+psycopg2://medivue:medivue@db:5432/medivue`

## Running Tests

Tests run against **SQLite** by default for fast, hermetic execution:

```bash
pytest -q
```

Rationale: tests should run quickly without requiring Docker. The application runtime uses PostgreSQL via `docker-compose.yml`.

## Design Decisions

### Tagging Implementation (Tasks ↔ Tags)

Implemented as a classic **many-to-many join table** (`task_tags`).

**Trade-offs vs PostgreSQL JSONB/ARRAY:**
- Join table is relationally correct, portable across DBs, enforces tag uniqueness, and supports indexes on tag names and associations.
- Efficient for queries like “tasks containing any of these tags” using joins.
- Slightly more schema complexity than JSONB/ARRAY.
- JSONB/ARRAY can be simpler for write paths, but filtering/indexing patterns can become more DB-specific.

### Delete Strategy

Implemented **Soft Delete** with `deleted_at` timestamp:
- Safer for production (auditability, avoids accidental data loss).
- Keeps referential integrity and supports future “undelete”.
- GET/list endpoints exclude soft-deleted tasks by default.

### Indexing

Added indexes for frequently-filtered fields:
- `tasks.priority`, `tasks.completed`, `tasks.due_date`, `tasks.deleted_at`
- Unique index on `tags.name`

## Production Readiness Improvements (if extended)

- Alembic migrations instead of create-on-start
- Structured logging + tracing (OpenTelemetry)
- AuthN/AuthZ (JWT/OAuth2) + RBAC
- Rate limiting / request throttling
- Background jobs for reminders/notifications
- Pagination defaults + cursor pagination at scale
- Centralized error correlation IDs
