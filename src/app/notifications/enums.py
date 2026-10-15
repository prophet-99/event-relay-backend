from enum import Enum


class NotificationStatus(str, Enum):
    PENDING = "PENDING"  # When is awaiting for taking by sqs worker
    SENDING = "SENDING"  # The worker take the message and process it
    PUBLISH_FAILED = (
        "PUBLISH_FAILED"  # The publisher could'nt send the message to the broker (SQS)
    )
    RETRY_SCHEDULED = "RETRY_SCHEDULED"  # When attempt_count < max_attempts
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    SENT = "SENT"


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
