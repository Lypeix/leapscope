# LeapScope

[![Tests](https://github.com/Lypeix/leapscope/actions/workflows/tests.yml/badge.svg)](https://github.com/Lypeix/leapscope/actions/workflows/tests.yml)

## Navigation

- [Documentation](#documentation)
- [Current Implementation](#current-implementation)
- [Key Files](#key-files)
- [Product Scope](#product-scope)
- [Privacy Boundary](#privacy-boundary)
- [Technology](#technology)
- [Project Structure](#project-structure)
- [How to Start](#how-to-start)

## Status

LeapScope is an in-development, privacy-conscious Windows activity analytics and
notification platform. The current implementation focuses on its containerized
backend foundation. Windows activity collection, offline synchronization, analytics,
and content notifications are planned for subsequent phases.

## Documentation

| Document | Purpose |
|---|---|
| [Product specification](./docs/PRODUCT.md) | Defines the user workflow, activity rules, privacy boundaries, and timezone behavior |
| [Roadmap](./docs/ROADMAP.md) | Tracks implementation milestones and the Phase 1 finish line |
| [Development log](./docs/DEVLOG.md) | Records learning sessions, completed work, and encountered problems |

## Current Implementation

- Containerized FastAPI and PostgreSQL services
- Environment-backed application settings
- SQLAlchemy engine and session management
- Alembic migration infrastructure
- Liveness and database-readiness endpoints
- User and device models with database migrations
- Account registration and login with Argon2 password hashing and JWT access tokens
- Authenticated current-user endpoint
- Dedicated PostgreSQL integration test database
- Automated testing through GitHub Actions

## Key Files

| File | Purpose |
|---|---|
| [`app/main.py`](./app/main.py) | Creates the FastAPI application and registers its routers |
| [`app/core/config.py`](./app/core/config.py) | Loads environment-backed application, database, and JWT settings |
| [`app/core/security.py`](./app/core/security.py) | Hashes and verifies passwords, and creates and validates JWT access tokens |
| [`app/api/dependencies.py`](./app/api/dependencies.py) | Authenticates bearer tokens and retrieves the current user |
| [`app/api/routers/auth.py`](./app/api/routers/auth.py) | Provides account registration and login endpoints |
| [`app/api/routers/users.py`](./app/api/routers/users.py) | Provides the authenticated `/users/me` endpoint |
| [`app/api/routers/health.py`](./app/api/routers/health.py) | Provides liveness and database-readiness endpoints |
| [`app/schemas/auth.py`](./app/schemas/auth.py) | Validates registration and login input and defines token responses |
| [`app/schemas/user.py`](./app/schemas/user.py) | Defines public user responses without password hashes |
| [`app/models/user.py`](./app/models/user.py) | Defines user accounts and their relationship to devices |
| [`app/models/device.py`](./app/models/device.py) | Defines device ownership, token-hash storage, and revocation timestamps |
| [`app/db/session.py`](./app/db/session.py) | Configures the SQLAlchemy engine, session factory, and database dependency |
| [`alembic/env.py`](./alembic/env.py) | Connects Alembic to application settings and model metadata |
| [`pyproject.toml`](./pyproject.toml) | Declares project dependencies, packaging, and pytest configuration |
| [`.env.example`](./.env.example) | Lists the environment variables needed for local setup |
| [`Dockerfile`](./Dockerfile) | Builds the API image and defines its startup command |
| [`docker-compose.yml`](./docker-compose.yml) | Configures the API, PostgreSQL, and optional test database |
| [`tests/conftest.py`](./tests/conftest.py) | Configures the API test client and test database sessions |
| [`tests/unit/test_security.py`](./tests/unit/test_security.py) | Tests Argon2 password hashing, verification, and randomized salts |
| [`tests/unit/test_jwt.py`](./tests/unit/test_jwt.py) | Tests JWT creation, expiration, and tampering rejection |
| [`tests/integration/test_health.py`](./tests/integration/test_health.py) | Tests API liveness and database readiness |
| [`.github/workflows/tests.yml`](./.github/workflows/tests.yml) | Applies and checks migrations, then runs the test suite in CI |

## Product Scope

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
- pwdlib with Argon2 and PyJWT
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
|-- .github/
|   `-- workflows/
|       `-- tests.yml
|-- alembic/
|   |-- README
|   |-- env.py
|   `-- script.py.mako
|-- app/
|   |-- api/
|   |   |-- routers/
|   |   |   |-- auth.py
|   |   |   |-- health.py
|   |   |   `-- users.py
|   |   `-- dependencies.py
|   |-- core/
|   |   |-- config.py
|   |   |-- logging_config.py
|   |   `-- security.py
|   |-- db/
|   |   |-- base.py
|   |   `-- session.py
|   |-- integrations/
|   |-- models/
|   |   |-- device.py
|   |   `-- user.py
|   |-- repositories/
|   |-- schemas/
|   |   |-- auth.py
|   |   `-- user.py
|   |-- services/
|   |-- static/
|   |   |-- css/
|   |   |   `-- app.css
|   |   `-- js/
|   |       `-- app.js
|   |-- tasks/
|   |   `-- celery_app.py
|   |-- templates/
|   `-- main.py
|-- collector/
|   |-- activity/
|   |-- local_queue/
|   |-- synchronization/
|   |-- config.py
|   `-- main.py
|-- docs/
|   |-- DEVLOG.md
|   |-- PRODUCT.md
|   `-- ROADMAP.md
|-- tests/
|   |-- collector/
|   |-- integration/
|   |   `-- test_health.py
|   |-- unit/
|   |   |-- test_jwt.py
|   |   `-- test_security.py
|   `-- conftest.py
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- docker-compose.yml
|-- Dockerfile
|-- pyproject.toml
`-- README.md
```

## How to Start

### Requirements

- Docker Desktop running with Linux containers

### Run with Docker Compose

1. Create the local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Build and start the API and PostgreSQL:

   ```powershell
   docker compose up -d --build --wait
   ```

3. Apply all database migrations:

   ```powershell
   docker compose exec api python -m alembic upgrade head
   ```

4. Open the API documentation at <http://127.0.0.1:8000/docs>.

The liveness and database-readiness endpoints are available at
<http://127.0.0.1:8000/health> and <http://127.0.0.1:8000/health/ready>.

Stop the services with:

```powershell
docker compose down
```

The PostgreSQL data remains in its Docker volume after the services stop.
