from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg.errors import UniqueViolation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_device
from app.db.session import get_db
from app.models import ActivitySession, Application, Device
from app.schemas import (
    ActivitySessionBatchIngest,
    ActivitySessionBatchResponse,
)


router = APIRouter(
    prefix="/collector",
    tags=["Collector"]
)


@router.post(
    "/sessions/batch",
    response_model=ActivitySessionBatchResponse,
    status_code=status.HTTP_200_OK
)
def ingest_sessions_batch(
    data: ActivitySessionBatchIngest,
    current_device: Annotated[Device, Depends(get_current_device)],
    session: Annotated[Session, Depends(get_db)]
) -> ActivitySessionBatchResponse:
    try:
        for item in data.sessions:
            application = session.scalar(
                select(Application).where(
                    Application.user_id == current_device.user_id,
                    Application.executable_name == item.executable_name
                )
            )

            if application is None:
                application = Application(
                    user_id=current_device.user_id,
                    executable_name=item.executable_name,
                    display_name=item.display_name
                )

                session.add(application)
                session.flush() # makes sure application gets its id before creating the activity_session below


            activity_session = ActivitySession(
                device_id=current_device.id,
                application_id=application.id,
                collector_event_id=item.collector_event_id,
                started_at=item.started_at,
                ended_at=item.ended_at
            )

            session.add(activity_session)

        session.commit()

    except IntegrityError as error: # triggers when inserts get rejected due to breaking a database integrity rule
        session.rollback()

        if isinstance(error.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The batch conflicts with existing records. No changes from this batch were saved"
            ) from error

        raise # raises the error if integrity error wasn't caused by UniqueViolation (which happens when eg. there r two identical device ids)

    return ActivitySessionBatchResponse(
        acknowledged_event_ids=[
            item.collector_event_id
            for item in data.sessions
        ]
    )