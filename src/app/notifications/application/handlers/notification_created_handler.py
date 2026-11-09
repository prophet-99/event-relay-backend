from datetime import datetime, timezone
from logging import Logger, getLogger
from typing import Any, cast

from sqlalchemy import CursorResult, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.notifications.application.dto.notification_message import NotificationMessage
from app.notifications.application.exceptions.delivery_exceptions import (
    NotificationAlreadySendingException,
    NotificationAlreadySentException,
    NotificationDeliveryException,
    NotificationNotFoundException,
)
from app.notifications.application.services.notification_publish_service import (
    NotificationPublishService,
)
from app.notifications.enums import NotificationStatus
from app.notifications.models import Notification
from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope

logger: Logger = getLogger(name=__name__)


class NotificationCreatedHandler:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    def handle(self, outbox_event_dto: OutboxEventEnvelope) -> None:
        try:
            claim_statement = (
                update(table=Notification)
                .where(
                    Notification.id == int(outbox_event_dto.aggregate_id),
                    Notification.status == NotificationStatus.PENDING,
                )
                .values(
                    status=NotificationStatus.SENDING,
                    attempt_count=Notification.attempt_count + 1,
                )
            )
            result: CursorResult[Any] = cast(
                typ=CursorResult[Any], val=self._db_session.execute(claim_statement)
            )
            if result.rowcount != 1:
                self._db_session.rollback()
                logger.warning(
                    msg="Notification is already taken by other node process"
                )

                db_notification = self._db_session.get(
                    entity=Notification, ident=int(outbox_event_dto.aggregate_id)
                )
                if (
                    db_notification
                    and db_notification.status == NotificationStatus.SENDING
                ):
                    raise NotificationAlreadySendingException()
                raise NotificationAlreadySentException()

            self._db_session.commit()

            statement = select(Notification).where(
                Notification.id == int(outbox_event_dto.aggregate_id),
            )
            db_notification: Notification | None = self._db_session.scalar(
                statement=statement
            )
            if db_notification is None:
                self._db_session.rollback()
                logger.warning(msg="Notification doesn't exist in the DB")
                raise NotificationNotFoundException()

            # PROCESS WITH STRATEGY PATTERN
            NotificationPublishService().publish_notification(
                notification_channel=db_notification.channel,
                notification_message=NotificationMessage(
                    destination=db_notification.destination,
                    message=db_notification.message,
                    payload=outbox_event_dto.payload,
                    user_id=db_notification.user_id,
                ),
            )
            db_notification.status = NotificationStatus.SENT
            db_notification.sent_at = datetime.now(tz=timezone.utc)
            self._db_session.commit()
        except SQLAlchemyError as exc:
            self._db_session.rollback()
            logger.exception(msg="An SQLAlchemy exception ocurred")
            raise NotificationDeliveryException() from exc
