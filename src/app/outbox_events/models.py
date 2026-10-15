from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import SqlAlchemyBase
from app.outbox_events.enums import OutboxEventStatus


class OutboxEvent(SqlAlchemyBase):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    aggregate_id: Mapped[str] = mapped_column(
        String(36), nullable=False
    )  # value of: notification.id
    aggregate_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # notification, user
    event_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True
    )  # UUID
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # notification.created
    status: Mapped[OutboxEventStatus] = mapped_column(
        Enum(OutboxEventStatus), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    max_publish_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    next_publish_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=None
    )
    publish_attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    last_publish_error: Mapped[str | None] = mapped_column(String(500), default=None)
