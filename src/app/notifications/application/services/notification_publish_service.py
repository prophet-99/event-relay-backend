from app.notifications.application.dto.notification_message import NotificationMessage
from app.notifications.application.strategies.notification_publish_push_email_strategy import (
    NotificationPublishEmailStrategy,
)
from app.notifications.application.strategies.notification_publish_push_strategy import (
    NotificationPublishPushStrategy,
)
from app.notifications.application.strategies.notification_publish_sms_strategy import (
    NotificationPublishSmsStrategy,
)
from app.notifications.application.strategies.notification_publish_strategy import (
    NotificationPublishStrategy,
)
from app.notifications.enums import NotificationChannel


class NotificationPublishService:
    def publish_notification(
        self,
        notification_channel: NotificationChannel,
        notification_message: NotificationMessage,
    ) -> None:
        strategies: dict[NotificationChannel, NotificationPublishStrategy] = {
            NotificationChannel.EMAIL: NotificationPublishEmailStrategy(),
            NotificationChannel.PUSH: NotificationPublishPushStrategy(),
            NotificationChannel.SMS: NotificationPublishSmsStrategy(),
        }
        strategies[notification_channel].send_notification(body=notification_message)
