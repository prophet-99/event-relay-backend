from app.notifications.application.dto.notification_message import NotificationMessage


class NotificationPublishSmsStrategy:
    def send_notification(self, body: NotificationMessage):
        print(f"Send SMS... {body.message}")
