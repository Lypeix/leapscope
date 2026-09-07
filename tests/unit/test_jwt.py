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