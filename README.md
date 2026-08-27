# LeapScope

[![Tests](https://github.com/Lypeix/leapscope/actions/workflows/tests.yml/badge.svg)](https://github.com/Lypeix/leapscope/actions/workflows/tests.yml)

## Status: In development

LeapScope is an in-development, privacy-conscious Windows activity analytics and
notification platform. The current implementation focuses on its containerized
backend foundation. Windows activity collection, offline synchronization, analytics,
and content notifications are planned for subsequent phases.

See: [Product specification](./PRODUCT.md) - [Roadmap](./ROADMAP.md) - [Development log](./DEVLOG.md)

## Current Implementation

- Containerized FastAPI and PostgreSQL services
- Environment-backed application settings
- SQLAlchemy engine and session management
- Alembic migration infrastructure
- Liveness and database-readiness endpoints
- Dedicated PostgreSQL integration test database
- Automated testing through GitHub Actions


### Activity Pipeline

```text
Windows collector
    -> local SQLite queue
    -> synchronization API
    -> PostgreSQL
    -> analytics dashboard
```

The collector will detect foreground application changes and idle periods, build
time-bounded activity sessions, preserve unsynchronized sessions locally, and upload
them in idempotent batches.

The backend will provide daily, weekly, and monthly usage totals, category breakdowns,
trends, session history, and a monthly Top 5 application ranking.


### Content Pipeline

```text
External APIs and feeds
    -> scheduled Celery tasks
    -> provider adapters
    -> notification rules
    -> in-app inbox and email
```

Users will be able to follow selected sources, receive publication notifications, and
discover updates related to applications they use frequently.

## Privacy Boundary

LeapScope is a personal analytics tool, not employee-monitoring software. The collector
will not record keystrokes or capture screen contents. Users will be able to exclude,
rename, and categorize applications, and synchronized data will belong to the
authenticated user and device that produced it.


## Technology

### Implemented

- Python
- FastAPI and Uvicorn
- Pydantic v2 and pydantic-settings
- SQLAlchemy 2.0 and Alembic
- PostgreSQL with psycopg 3
- pytest
- GitHub Actions
- Docker Compose

### Planned

- Celery, Celery Beat, and Redis
- HTTPX and RSS/Atom integrations
- pywin32 and psutil
- SQLite collector queue
- PyInstaller
- Jinja2
- HTML, CSS, and JavaScript
- Chart.js


## Project Structure

```text
leapscope/
|-- app/
|   |-- api/
|   |   `-- routers/
|   |-- core/
|   |-- db/
|   |-- integrations/
|   |-- models/
|   |-- repositories/
|   |-- schemas/
|   |-- services/
|   |-- static/
|   |-- tasks/
|   |-- templates/
|   `-- main.py
|-- collector/
|   |-- activity/
|   |-- local_queue/
|   |-- synchronization/
|   `-- main.py
|-- tests/
|   |-- collector/
|   |-- integration/
|   `-- unit/
|-- .github/workflows/
|-- docker-compose.yml
|-- Dockerfile
|-- PRODUCT.md
|-- pyproject.toml
|-- DEVLOG.md
`-- ROADMAP.md
```
