from pwdlib import PasswordHash

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"


password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    return password_hasher.hash(plain_password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.access_token_expire_minutes
        ),
        "token_type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM
    )

def decode_access_token(token: str) -> UUID:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={
                "require": ["sub", "iat", "exp", "token_type"]
            }
        )

        if payload["token_type"] != "access":
            raise InvalidTokenError("Expected an access token")

        return UUID(payload["sub"])

    except (ValueError, TypeError, OverflowError) as error:
        raise InvalidTokenError(
            "invalid access token claims"
        ) from error
