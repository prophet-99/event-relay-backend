from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import SqlAlchemyBase
from app.notifications.enums import NotificationChannel, NotificationStatus


class Notification(SqlAlchemyBase):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel), nullable=False
    )
    destination: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    next_retry_attempt: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(String(100), default=None)
    parent_notification_id: Mapped[int | None] = mapped_column(
        ForeignKey("notifications.id"), default=None
    )
    parent_notification: Mapped["Notification | None"] = relationship(
        "Notification", remote_side=[id], back_populates="retry_notifications"
    )
    retry_notifications: Mapped["list[Notification]"] = relationship(
        "Notification", back_populates="parent_notification"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
