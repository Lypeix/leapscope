from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select

from app.core.security import (
    create_access_token,
    generate_collector_token,
    hash_collector_token,
)
from app.models import ActivitySession, Application, Device, User


@pytest.fixture # nesting reason: pytest handles the database dependency once, while your tests get a convenient actor factory they can call repeatedly.
def make_actor(db_session):
    def create(user=None):
        if user is None:
            user = User(
                email=f"{uuid4()}@example.com",
                password_hash="unused-in-these-tests"
            )
            db_session.add(user)
            db_session.flush()

        token = generate_collector_token()
        device = Device(
            user_id=user.id,
            name="Test PC",
            token_hash=hash_collector_token(token)
        )
        db_session.add(device)
        db_session.flush()

        return {
            "user": user,
            "device": device,
            "user_headers": {
                "Authorization": f"Bearer {create_access_token(user.id)}"
            },
            "collector_headers": {
                "Authorization": f"Bearer {token}"
            }
        }
    return create


def make_event(**changes):
    event = {
        "collector_event_id": str(uuid4()),
        "executable_name": "Sun.exe",
        "started_at": "2026-09-23T09:00:00Z",
        "ended_at": "2026-09-23T09:54:00Z", 
    }
    event.update(changes)
    return event


def upload(client, actor, events):
    return client.post(
        "/collector/sessions/batch",
        headers=actor["collector_headers"],
        json={"sessions": events}
    )