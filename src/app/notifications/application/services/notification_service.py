from logging import getLogger
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.notifications.constants import MAX_SEND_ATTEMPTS
from app.notifications.enums import NotificationStatus
from app.notifications.exceptions import DatabaseException
from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate, NotificationResponse
from app.outbox_events.constants import MAX_PUBLISH_ATTEMPTS
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent

logger = getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self._db = db

    def create(
        self, notification_request: NotificationCreate, user_owner_id: int
    ) -> NotificationResponse:
        new_notification = Notification(
            **notification_request.model_dump(),
            status=NotificationStatus.PENDING,
            max_attempts=MAX_SEND_ATTEMPTS,
            user_id=user_owner_id,
        )

        try:
            self._db.add(new_notification)
            self._db.flush()

            new_outbox_event = OutboxEvent(
                aggregate_id=str(new_notification.id),
                aggregate_type="notification",
                event_id=str(uuid4()),
                event_type="notification.created",
                status=OutboxEventStatus.PENDING,
                payload={},
                max_publish_attempts=MAX_PUBLISH_ATTEMPTS,
            )
            self._db.add(new_outbox_event)

            self._db.refresh(new_notification)
            self._db.commit()

            return NotificationResponse.model_validate(new_notification)
        except SQLAlchemyError as exc:
            self._db.rollback()
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseException() from exc
