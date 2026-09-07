from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import Settings


TEST_KEY = "test-only-" + "a" * 64

@pytest.fixture(autouse=True)
def jwt_settings(monkeypatch):
    settings = Settings(
        _env_file=None,
        database_url="sqlite://",
        jwt_secret_key=TEST_KEY,
        access_token_expire_minutes=5
    )

    monkeypatch.setattr(
        security,
        "get_settings",
        lambda: settings
    )

    return settings


@pytest.fixture
def claims():
    now = datetime.now(UTC)

    return {
        "sub": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "token_type": "access"
    }


def sign(claims):
    return jwt.encode(claims, TEST_KEY, algorithm="HS256")


def test_access_token_round_trip(jwt_settings):
    user_id = uuid4()

    token = security.create_access_token(user_id)
    payload = jwt.decode(
        token,
        TEST_KEY,
        algorithms=["HS256"]
    )

    assert security.decode_access_token(token) == user_id

    assert payload["exp"] - payload["iat"] == (
        jwt_settings.access_token_expire_minutes * 60
    )


def test_expired_token_is_rejected(claims):
    claims["iat"] = datetime.now(UTC) - timedelta(hours=1)
    claims["exp"] = datetime.now(UTC) - timedelta(minutes=1)

    token = sign(claims)

    with pytest.raises(InvalidTokenError):
        security.decode_access_token(token)


def test_modified_payload_is_rejected(claims):
    original_token = sign(claims)
    header, _, original_signature = original_token.split(".")

    claims["sub"] = str(uuid4())
    changed_token = sign(claims)
    _, changed_payload, _ = changed_token.split(".")

    tampered_token = (
        f"{header}.{changed_payload}.{original_signature}"
    )

    with pytest.raises(InvalidTokenError):
        security.decode_access_token(tampered_token)

        