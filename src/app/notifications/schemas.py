from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.notifications.enums import NotificationChannel, NotificationStatus


class NotificationBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    message: str = Field(min_length=1)
    channel: NotificationChannel
    destination: str = Field(min_length=1)


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: NotificationStatus
    created_at: datetime
    updated_at: datetime | None
    sent_at: datetime | None
    next_retry_attempt: datetime | None
    error_message: str | None
    parent_notification: "NotificationResponse | None"
