from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@router.get("/ready")
def readiness(
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error # connects the public HTTPException to the original SQLAlchemy error

    return {
        "status": "ready",
        "database": "reachable"
    }

