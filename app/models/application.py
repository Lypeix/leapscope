from __future__ import annotations

from datetime import datetime

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING: # avoids circular import
    from app.models.user import User

class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint( # for a given user, the same executable name can appear only once, eg. "chrome.exe"
            "user_id",
            "executable_name",
            name="uq_applications_user_executable" # gives constraint an explicit name for later debugging
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE")
    )

    executable_name: Mapped[str] = mapped_column(
        String(255)
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user: Mapped[User] = relationship()