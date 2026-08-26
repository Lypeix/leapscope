# LeapScope Development Log

## Day 1 - 21.08.2026 

### Session 1 (18:05-20:15)

- Reviewed and revised the initial Codex-generated project planning and scaffolding
- Selected the LeapScope product name
- Drafted the initial product scope and privacy boundary
- Drafted the activity and content-processing pipelines
- Selected the initial backend, collector, frontend, testing, and infrastructure stack
- Created the initial multi-component project structure
- Defined the Phase 1 finish line and milestone-based roadmap
- Added placeholder files while leaving learning-critical configuration unimplemented

## Day 2 - 22.08.2026

### Session 1 (08:05-09:24)
- Created `PRODUCT.md`
- Defined Phase 1 user workflow
- Defined what counts as an `activity session`
- Defined when the user enters an `idle state`
- Expanded idle-time rules to distinguish user inactivity from verified foreground media playback
- Defined behavior when multiple windows are opened
- Defined when activity sessions start and finish
- Defined session boundary rules
- Checked the commit with `git diff --cached`
- Decided which application information may be stored
- Defined application exclusion and privacy rules
- Reviewed PRODUCT.md additions

### Session 2 (19:00-19:26)
- Drew the collector-to-database data flow
- Defined UTC storage and user reporting-timezone behavior

## DAY 3 - 23.08.2026

### Break Day

## DAY 4 - 24.08.2026

### Session 1 (07:39-8:19)
- Created `.venv` virtual environment
- Temporarily bypassed PowerShell execution policy to activate virtual environment 
- Venv gives LeapScope its own private python package, so that updates wont interfere with other projects
- Fixed a setuptools package discovery error caused by lack of `pyproject.toml` configuration
- Added `FastAPI` n `Uvicorn` as the initial dependencies for `pyproject.toml`
- Created FastAPI application and configured its asynchronous lifespan handler inside `app/main.py`

### Session 2 (18:33-19:22)
- Changed lifespan return annotation from AsyncIterator[None] to AsyncGenerator[None, None] in `app/main.py` because:
    1. Pylance gave deprecation warning for asynccontextmanager
    2. The function uses `async def` and `yield` making it specifically an asynchronous generator
- Added `pydantic-settings` dependency to `pyproject.toml`
- Installed `pydantic-settings`
- Configured Settings class inside `app/core/config.py`
- Cached `get_settings()` with `lru_cache` so application reuses one settings instance instead of constructing it repeatedly
- Loaded the cached settings in `app/main.py`
- Configured the app title and debug mode through environment-backed settings

## DAY 5 - 25.08.2026

### Session 1 (18:49-19:27)
- Added `.dockerignore` so that Docker doesn't end up using whole .venv, .git, etc. just to build one tiny API image
- Wrote the API Dockerfile
- Successfully installed and configured WSL 2
- Successfully installed and configured Docker Desktop 
- Built `leapscope-api` Docker image
- Ran the API inside a container with port `8000` mapped to the host
- Successfully opened the containerized API documentation through SwaggerUI

## DAY 6 - 26.08.2026

### Session 1 (16:21-x)
- Fixed formatting for two earlier sessions
- Created `.env.example` and `.env`
- Generated password and confirmed `.env` is ignored, and hidden
- Added `PostgreSQL 18` to `Docker Compose`
- Configured `PostgreSQL 18` database, user, password, port, volume and healthcheck inside `docker-compose.yml`
- Successfully started `PostgreSQL` inside `Docker Compose` and verified the database connection through executing a SQL query inside the container
