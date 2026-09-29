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


def test_duplicate_uploads_store_one_session(client, db_session, make_actor):
    actor = make_actor() # defining actor individually for each test so that each test gets its fresh isolated setup
    event = make_event(
        started_at="2026-09-23T11:00:00+02:00", 
        ended_at="2026-09-23T11:05:00+02:00"
    )

    

    for batch in ([event, event], [event]):
        response = upload(client, actor, batch)

        assert response.status_code == 200, response.text
        assert response.json()["acknowledged_event_ids"] == [
            event["collector_event_id"]
        ]

    count = db_session.scalar(
        select(func.count()).select_from(ActivitySession)
    )
    assert count == 1

    history = client.get("/sessions", headers=actor["user_headers"])
    assert history.status_code == 200, history.text

    rows = history.json()
    assert len(rows) == 1
    assert rows[0]["collector_event_id"] == event["collector_event_id"]

    started_at = datetime.fromisoformat(rows[0]["started_at"])
    ended_at = datetime.fromisoformat(rows[0]["ended_at"])

    assert started_at == datetime(2026, 9, 23, 9, 0, tzinfo=UTC)
    assert ended_at == datetime(2026, 9, 23, 9, 5, tzinfo=UTC)
    assert started_at.utcoffset() == timedelta(0)
    assert ended_at.utcoffset() == timedelta(0)


def test_conflicting_duplicate_rolls_back_batch(client, db_session, make_actor):
    actor = make_actor()

    original = make_event(collector_event_id=str(UUID(int=2)))
    response = upload(client, actor, [original])
    assert response.status_code == 200, response.text

    new_event = make_event(
        collector_event_id=str(UUID(int=1)),
        executable_name="firefox.exe",
        started_at="2026-09-23T10:00:00Z",
        ended_at="2026-09-23T10:05:00Z"
    )
    
    changed_event = {
        **original,
        "ended_at": "2026-09-23T09:10:00Z"
    }

    response = upload(client, actor, [new_event, changed_event])
    assert response.status_code == 409, response.text

    stored = db_session.scalars(select(ActivitySession)).all()
    
    assert len(stored) == 1
    assert stored[0].collector_event_id == UUID(original["collector_event_id"])
    assert stored[0].ended_at == datetime.fromisoformat(
        original["ended_at"].replace("Z", "+00:00")
    )

    executables = db_session.scalars(
        select(Application.executable_name)
    ).all()
    assert executables == ["sun.exe"]


def test_sessions_are_scoped_to_their_owner(
    client, db_session, make_actor
):
    alice = make_actor()
    alice_laptop = make_actor(user=alice["user"])
    bob = make_actor()

    event = make_event()

    for actor in (alice, alice_laptop, bob):
        submitted = dict(event)

        if actor is alice_laptop:
            submitted.update(
                started_at="2026-09-23T10:00:00Z",
                ended_at="2026-09-23T10:05:00Z",
            )

        response = upload(client, actor, [submitted])
        assert response.status_code == 200, response.text

    alice_response = client.get(
        "/sessions", headers=alice["user_headers"]
    )
    bob_response = client.get(
        "/sessions", headers=bob["user_headers"]
    )
    assert alice_response.status_code == 200
    assert bob_response.status_code == 200

    alice_rows = alice_response.json()
    bob_rows = bob_response.json()

    assert [row["device_id"] for row in alice_rows] == [
        str(alice_laptop["device"].id),
        str(alice["device"].id),
    ]
    assert len(bob_rows) == 1
    assert bob_rows[0]["device_id"] == str(bob["device"].id)

    assert alice_rows[0]["application_id"] == alice_rows[1]["application_id"]
    assert alice_rows[0]["application_id"] != bob_rows[0]["application_id"]

    page = client.get(
        "/sessions",
        headers=alice["user_headers"],
        params={"limit": 1, "offset": 1},
    )
    assert page.status_code == 200
    assert page.json() == alice_rows[1:2]

    assert client.get("/sessions").status_code == 401
    assert client.get(
        "/sessions", headers=alice["collector_headers"]
    ).status_code == 401

    forged_event = make_event(device_id=str(bob["device"].id))
    rejected = upload(client, alice, [forged_event])
    assert rejected.status_code == 422

    count = db_session.scalar(
        select(func.count()).select_from(ActivitySession)
    )
    assert count == 3


@pytest.mark.parametrize(
    "changes",
    [
        {"started_at": "2026-09-23T09:00:00"},
        {"ended_at": "2026-09-23T09:05:00"},
        {"started_at": "not-a-timestamp"},
        {"ended_at": "2026-09-23T09:00:00Z"},
        {"ended_at": "2026-09-23T08:59:00Z"},
    ],
    ids=[
        "naive-start",
        "naive-end",
        "malformed-timestamp",
        "zero-duration",
        "negative-duration"
    ],
)
def test_invalid_timestamp_are_rejected(
    client, db_session, make_actor, changes
):
    actor = make_actor()
    response = upload(client, actor, [make_event(**changes)])

    assert response.status_code == 422, response.text

    count = db_session.scalar(
        select(func.count()).select_from(ActivitySession)
    )
    
    assert count == 0