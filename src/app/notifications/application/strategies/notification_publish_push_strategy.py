from app.notifications.application.dto.notification_message import NotificationMessage


class NotificationPublishPushStrategy:
    def send_notification(self, body: NotificationMessage):
        print(f"Send Push notification... {body.message}")
