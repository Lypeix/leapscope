from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Device, User
from app.schemas import DeviceRead, DeviceRegister


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