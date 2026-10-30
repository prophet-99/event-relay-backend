from typing import Protocol

from app.notifications.application.dto.notification_message import NotificationMessage


class NotificationPublishStrategy(Protocol):
    def send_notification(self, body: NotificationMessage) -> None: ...
