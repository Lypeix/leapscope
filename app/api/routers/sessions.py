from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import ActivitySession, Device, User
from app.schemas import ActivitySessionRead


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


@router.get("", response_model=list[ActivitySessionRead])
def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0
) -> list[ActivitySession]:
    
    statement = (
        select(ActivitySession)
        .join(ActivitySession.device)
        .where(Device.user_id == current_user.id) # ownership detection
        .order_by(
            ActivitySession.started_at.desc(),
            ActivitySession.id.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    return list(session.scalars(statement).all())