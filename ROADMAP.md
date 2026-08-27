# LeapScope Roadmap

> This roadmap will be evolving during the production process

Target: a usable, deployed first release by mid-November 2026.

## Phase 1: First End-to-End Activity Pipeline

### Phase 1 Finish Line

- Docker Compose starts the API and PostgreSQL
- Alembic applies all migrations to an empty PostgreSQL database
- A user can register and authenticate
- A user can register a collector device and receive a revocable collector token
- The Windows collector detects foreground applications and idle time
- Sessions survive temporary network failure in a local SQLite queue
- Sessions synchronize without creating duplicates
- The API returns session history and basic daily totals
- Automated tests run through GitHub Actions

### Product Contract

- [x] Select the LeapScope name
- [x] Define the initial product boundary
- [x] Create the initial multi-component project structure
- [x] Initialize Git and create the GitHub repository
- [x] Define the Phase 1 user workflow
- [x] Define what counts as an activity session
- [x] Decide when a session starts and finishes
- [x] Define idle-time behavior
- [x] Decide which application information may be stored
- [x] Define application exclusion and privacy rules
- [x] Draw the collector-to-database data flow
- [x] Define UTC storage and user reporting-timezone behavior

### FastAPI, Docker, And PostgreSQL

- [x] Create and activate the virtual environment
- [x] Add dependencies gradually to `pyproject.toml`
- [x] Create the FastAPI application and lifespan
- [x] Add environment-backed settings
- [x] Write the API Dockerfile
- [x] Add PostgreSQL to Docker Compose
- [x] Add the API to Docker Compose
- [x] Learn Docker images, containers, ports, volumes, and networks
- [x] Configure the SQLAlchemy engine and session factory
- [x] Initialize Alembic
- [x] Add health and database-readiness endpoints
- [x] Configure the dedicated PostgreSQL test database
- [x] Create the initial pytest and TestClient setup
- [x] Add GitHub Actions for tests
- [x] Verify the API locally and through Docker

### Reconstruction And Buffer

- [ ] Reconstruct the Docker and database foundation locally
- [ ] Explain how the API reaches PostgreSQL through the Docker network
- [ ] Explain what persists when containers are removed
- [ ] Review and document encountered failures
- [ ] Use this milestone as recovery time if earlier work took longer

### Users, Devices, And Authentication

- [ ] Create `User` and `Device` models
- [ ] Generate and apply their migration
- [ ] Create registration and login schemas
- [ ] Hash passwords using Argon2
- [ ] Issue and validate JWT access tokens
- [ ] Add `POST /auth/register`
- [ ] Add `POST /auth/login`
- [ ] Add `GET /users/me`
- [ ] Add collector-device registration
- [ ] Generate revocable collector tokens
- [ ] Store collector tokens as hashes
- [ ] Test authentication and resource ownership

### Review And Buffer

- [ ] Reconstruct the authentication flow
- [ ] Explain password hashing versus encryption
- [ ] Explain JWT authentication versus collector tokens
- [ ] Review database relationships and ownership
- [ ] Catch up or stop early if mentally saturated

### Activity Storage And Ingestion

- [ ] Create `Application` and `ActivitySession` models
- [ ] Store activity-session timestamps in UTC according to the product contract
- [ ] Enforce unique collector event identifiers per device
- [ ] Generate and apply the activity migration
- [ ] Add batch session-ingestion schemas
- [ ] Add `POST /collector/sessions/batch`
- [ ] Reject invalid and negative session durations
- [ ] Prevent duplicate session ingestion
- [ ] Enforce device and user ownership
- [ ] Add `GET /sessions`
- [ ] Test duplicates, ownership, and invalid timestamps

### Windows Collector Prototype

- [ ] Detect the foreground window with `pywin32`
- [ ] Resolve process information with `psutil`
- [ ] Detect idle time
- [ ] Implement session start and finish transitions
- [ ] Handle switching between applications
- [ ] Handle collector shutdown
- [ ] Avoid recording excluded applications
- [ ] Unit-test session transition logic separately from Windows APIs
- [ ] Add collector configuration for API URL, collector token, idle threshold, and local exclusions

### Offline Queue And Synchronization

- [ ] Create the local SQLite queue
- [ ] Save completed sessions before uploading
- [ ] Upload sessions in batches using HTTPX
- [ ] Mark successfully synchronized sessions
- [ ] Retain sessions after failed synchronization
- [ ] Retry safely without creating duplicates
- [ ] Test offline collection followed by reconnection

### First Analytics Endpoint

- [ ] Add daily application totals
- [ ] Group session durations by application
- [ ] Add `GET /analytics/daily`
- [ ] Test daily totals across midnight and timezone boundaries
- [ ] Document known Phase 1 analytics limitations

### Integration And Demonstration

- [ ] Run the project from a clean clone
- [ ] Start API and PostgreSQL through Docker Compose
- [ ] Apply all migrations to an empty database
- [ ] Register a user and collector device
- [ ] Record real application switches
- [ ] Disconnect and reconnect synchronization
- [ ] Confirm sessions appear in PostgreSQL
- [ ] Retrieve daily totals through the API
- [ ] Run the complete test suite
- [ ] Verify GitHub Actions passes on a clean push