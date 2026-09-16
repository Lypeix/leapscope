from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.device import Device


class ActivitySession(Base):
    __tablename__ = "activity_sessions"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    device_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("devices.id", ondelete="CASCADE"),
        index=True
    )

    application_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True
    )

    collector_event_id: Mapped[UUID] = mapped_column(
        Uuid
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    device: Mapped[Device] = relationship()
    application: Mapped[Application] = relationship()