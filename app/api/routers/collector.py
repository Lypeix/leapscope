from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
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
    application_names: dict[str, str | None] = {}

    for item in data.sessions:
        application_names.setdefault(
            item.executable_name,
            item.display_name
        )

    application_ids = {}
    
    try:
        for executable_name in sorted(application_names):
            session.execute(
                insert(Application)
                .values(
                    user_id=current_device.user_id,
                    executable_name=executable_name,
                    display_name=application_names[executable_name],
                )
                .on_conflict_do_nothing( # skips insert if the same user has two instances of the same executable
                    constraint="uq_applications_user_executable"
                )
            )

            application_ids[executable_name] = session.execute(
                select(Application.id).where(
                    Application.user_id == current_device.user_id, # application is database representation of an executable
                    Application.executable_name == executable_name
                )
            ).scalar_one() # extracts the actual Application.id value from the first selected column 


        for item in sorted(
            data.sessions,
            key=lambda item: item.collector_event_id, # lambda tells sorted() to use each session's collector_event_id as the sorting key 
        ):
            application_id = application_ids[item.executable_name]

            inserted_id = session.scalar(
                insert(ActivitySession)
                .values(
                    device_id=current_device.id,
                    application_id=application_id,
                    collector_event_id=item.collector_event_id,
                    started_at=item.started_at,
                    ended_at=item.ended_at
                )
                .on_conflict_do_nothing(
                    constraint="uq_activity_sessions_device_event",
                )
                .returning(ActivitySession.id)
            )

            if inserted_id is None:
                existing = session.execute(
                    select(ActivitySession).where(
                        ActivitySession.device_id == current_device.id,
                        ActivitySession.collector_event_id == item.collector_event_id
                    )
                ).scalar_one()

                if (
                    existing.application_id != application_id
                    or existing.started_at != item.started_at
                    or existing.ended_at != item.ended_at
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, # bc data wouldnt match
                        detail=f"Event {item.collector_event_id} already exists with different activity data."
                    )

        session.commit()

    except (SQLAlchemyError, HTTPException):
        session.rollback() # undoes the whole transaction incase an important error gets raised
        raise

    return ActivitySessionBatchResponse(
        acknowledged_event_ids=list(
            dict.fromkeys( # fromkeys deletes duplicates while preserving existing ordering
                item.collector_event_id
                for item in data.sessions
            )
        )
    )
