# LeapScope Product Contract

## Phase 1 User Workflow

1. The user starts the LeapScope backend and Windows collector.
2. The user registers an account through the API.
3. The user logs in and receives an access token.
4. The user registers the current computer as a collector device.
5. LeapScope generates a separate revocable device token.
6. The user places the device token in the collector configuration.
7. The user configures the idle threshold and optional application exclusions.
8. The user starts the collector and uses the computer normally.
9. The collector automatically detects foreground application changes and idle time.
10. Completed activity sessions are saved to the local SQLite queue.
11. The collector periodically synchronizes queued sessions with the backend.
12. The backend validates and stores sessions without accepting duplicates.
13. The user requests session history through the API.
14. The user requests daily application totals through the API.
15. The user can revoke a collector device, preventing further synchronization.

## Offline Workflow

1. The backend becomes temporarily unavailable.
2. The collector continues recording completed sessions locally.
3. Failed uploads remain pending in the SQLite queue.
4. The collector retries synchronization later.
5. The backend recognizes already accepted event identifiers.
6. No session is lost or stored twice.

## Phase 1 Interface

Phase 1 is operated through the FastAPI API and Swagger UI. The graphical dashboard
will be implemented in a later phase.


