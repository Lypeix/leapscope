from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import decode_access_token, hash_collector_token 
from app.db.session import get_db
from app.models import User, Device

bearer_scheme = HTTPBearer()

def get_current_user( # for requests on behalf of human users
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError as error:
        raise authentication_error from error

    user = session.get(User, user_id)

    if user is None:
        raise authentication_error

    return user

collector_bearer_scheme = HTTPBearer(
    scheme_name="CollectorToken"
)


def get_current_device( # for automatic requests on behalf of the Windows collector
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(collector_bearer_scheme)],
    session: Annotated[Session, Depends(get_db)]
) -> Device:
    token_hash = hash_collector_token(
        credentials.credentials
    )

    device = session.scalar( # means: dear postgresql, find me a device whose stored token_hash matches this submitted token's hash, and which has not been revoked
        select(Device).where(
            Device.token_hash == token_hash,
            Device.revoked_at.is_(None)
        )
    )

    if device is None:
        raise HTTPException( # means: dear postgresql, if you havent found the requested device, raise a 401_UNAUTHORIZED error
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked collector token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return device