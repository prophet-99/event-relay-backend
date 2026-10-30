from app.notifications.application.dto.notification_message import NotificationMessage


class NotificationPublishEmailStrategy:
    def send_notification(self, body: NotificationMessage):
        print(f"Send Email... {body.message}")
