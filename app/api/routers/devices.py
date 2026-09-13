from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user

from app.db.session import get_db
from app.models import Device, User
from app.schemas import DeviceRead, DeviceRegister, CollectorTokenResponse

from app.core.security import generate_collector_token, hash_collector_token

from datetime import UTC, datetime
from uuid import UUID


router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)


@router.post(
    "",
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED
)

def register_device(
    device_data: DeviceRegister,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
) -> Device:

    device = Device(
        user_id=current_user.id,
        name=device_data.name,
        token_hash=None
    )

    session.add(device)
    session.commit()
    session.refresh(device) # ensures the returned object has the latest values

    return device


@router.post(
    "/{device_id}/token",
    response_model=CollectorTokenResponse,
    status_code=status.HTTP_201_CREATED
)

def issue_collector_token( # issuance happens one for each device record
    device_id: UUID,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
) -> CollectorTokenResponse:
    device = session.scalar(
        select(Device)
        .where(
            Device.id == device_id, # checks if the device exists
            Device.user_id == current_user.id # checks if it actually belongs to the current user
        )
        .with_for_update() # protects against concurrent updates/race conditions that could overwrite each other in this transaction
    )

    if device is None: # means the query from earlier found nothing
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if device.revoked_at is not None: # checks whether collector token for this device has previously been revoked
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device has been revoked"
        )

    if device.token_hash is not None: # checks whether device already has an issued token (through hash because only hash is stored)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This device already has a collector token"
        )


    token = generate_collector_token()
    device.token_hash = hash_collector_token(token)

    session.commit()

    response.headers["Cache-Control"] = "no-store" # tells tells browsers, proxies and other HTTP caches to not store this response bc it contains a secret credential

    return CollectorTokenResponse(
        device_id=device.id,
        collector_token=token
    )


@router.post(
    "/{device_id}/revoke",
    response_model=DeviceRead
)

def revoke_device(
    device_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
) -> Device:

    device = session.scalar(
        select(Device)
        .where(
            Device.id == device_id,
            Device.user_id == current_user.id
        )
        .with_for_update()
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if device.revoked_at is None: # .revoked_at attribute refers to Device model inside app `app/models/devices.py`
        device.revoked_at = datetime.now(UTC)
        session.commit()

    return device