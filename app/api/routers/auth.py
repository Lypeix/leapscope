from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import TokenResponse, UserRead, UserRegister, UserLogin

DUMMY_PASSWORD_HASH = hash_password("dummy-login-password")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegister,
    session: Annotated[Session, Depends(get_db)],
) -> User:
    user = User(
        email=data.email,
        password_hash=hash_password(
            data.password.get_secret_value()
        ),
        reporting_timezone=data.reporting_timezone,
    )

    session.add(user)

    try: 
        session.commit()
    except IntegrityError as error:
        session.rollback()

        existing_user_id = session.scalar(
            select(User.id).where(User.email == data.email)
        )

        if existing_user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered on an existing account"
            ) from error

        raise

    session.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: UserLogin,
    session: Annotated[Session, Depends(get_db())]
) -> TokenResponse:
    user = session.scalar(
        select(User).where(User.email == data.email)
    )

    password_hash = (
        user.password_hash
        if user is not None
        else DUMMY_PASSWORD_HASH
    )

    password_matches = verify_password(
        data.password.get_secret_value(),
        password_hash
    )

    if user is None or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )