# LeapScope

## Status: In development

LeapScope is a privacy-conscious Windows activity analytics and notification platform.
It records foreground application sessions as they happen, synchronizes them to a
FastAPI backend, produces usage analytics, and monitors selected external sources for
relevant updates.

See: [DEVLOG.md](./DEVLOG.md)

## Product Scope

LeapScope contains two independent but connected pipelines.

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

## Planned Technology

### Backend

- Python
- FastAPI and Uvicorn
- Pydantic v2 and pydantic-settings
- SQLAlchemy 2.0 and Alembic
- PostgreSQL with psycopg 3
- Celery, Celery Beat, and Redis
- HTTPX and RSS/Atom integrations

### Windows Collector

- Python
- pywin32 and psutil
- SQLite offline queue
- HTTPX synchronization
- PyInstaller packaging

### Frontend

- Jinja2
- Semantic HTML and responsive CSS
- Vanilla JavaScript and Fetch API
- Chart.js

### Quality

- pytest and pytest-cov
- Ruff
- mypy
- GitHub Actions
- Docker Compose

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
