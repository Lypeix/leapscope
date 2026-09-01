from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.device import Device


class User(Base):
    __tablename__ = "users"


    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    reporting_timezone: Mapped[str] = mapped_column(
        String(70),
        default="UTC",
        server_default="UTC"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    devices: Mapped[list[Device]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )