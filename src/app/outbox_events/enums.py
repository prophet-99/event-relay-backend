from enum import Enum


class OutboxEventStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHING = "PUBLISHING"
    PUBLISH_RETRY_SCHEDULED = "PUBLISH_RETRY_SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
