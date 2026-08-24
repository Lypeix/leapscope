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
- Created FastAPI application and configured its asynchronous lifespan handler inside `main.py`

## Session 2 (18:33-x)
- In `main.py` changed lifespan return annotation from AsyncIterator[None] to AsyncGenerator[None, None] because:
    1. Pylance gave deprecation warning for asynccontextmanager
    2. The function uses `async def` and `yield` making it specifically an asynchronous generator