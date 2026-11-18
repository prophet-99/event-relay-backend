from datetime import datetime
from logging import getLogger
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.notifications.application.exceptions.persistence_exceptions import (
    DatabaseException,
    NotificationMustFailedStatusException,
)
from app.notifications.constants import MAX_SEND_ATTEMPTS
from app.notifications.enums import NotificationStatus
from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate, NotificationResponse
from app.outbox_events.constants import MAX_PUBLISH_ATTEMPTS
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent

logger = getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self._db = db

    def get_by_range(
        self,
        *,
        user_owner_id: int,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[NotificationResponse]:
        filters = [
            Notification.user_id == user_owner_id,
        ]
        if start_date is not None:
            filters.append(Notification.created_at >= start_date)
        if end_date is not None:
            filters.append(Notification.created_at <= end_date)

        statement = select(Notification).where(*filters)
        notifications = self._db.scalars(statement=statement).all()

        return [
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]

    def _create_outbox_event(self, *, notification_id: str) -> OutboxEvent:
        """Create an OutboxEvent, the complete transaction (commit and rollback) must be in the parent"""
        try:
            new_outbox_event = OutboxEvent(
                aggregate_id=notification_id,
                aggregate_type="notification",
                event_id=str(uuid4()),
                event_type="notification.created",
                status=OutboxEventStatus.PENDING,
                payload={},
                max_publish_attempts=MAX_PUBLISH_ATTEMPTS,
            )
            self._db.add(instance=new_outbox_event)

            return new_outbox_event
        except SQLAlchemyError as exc:
            logger.exception(msg="SQLAlchemyError Exception")

            raise DatabaseException() from exc

    def create(
        self, *, user_owner_id: int, notification_request: NotificationCreate
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

            self._create_outbox_event(notification_id=str(new_notification.id))

            self._db.refresh(new_notification)
            self._db.commit()

            return NotificationResponse.model_validate(new_notification)
        except SQLAlchemyError as exc:
            self._db.rollback()
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseException() from exc

    def clone_from_parent(
        self,
        *,
        notification_id: int,
        user_owner_id: int,
        notification_request: NotificationCreate,
    ) -> NotificationResponse:
        try:
            statement = select(Notification).where(
                Notification.id == notification_id,
                Notification.status == NotificationStatus.FAILED,
                Notification.user_id == user_owner_id,
            )
            notification: Notification | None = self._db.scalar(statement=statement)
            if notification is None:
                logger.exception(
                    msg=f"The notification: {notification_id}, doesn't exists or isn't in the FAILED status"
                )
                raise NotificationMustFailedStatusException()

            clone_notification = Notification(
                **notification_request.model_dump(),
                status=NotificationStatus.PENDING,
                max_attempts=MAX_SEND_ATTEMPTS,
                user_id=user_owner_id,
                parent_notification_id=notification.id,
            )
            self._db.add(instance=clone_notification)
            self._db.flush()

            self._create_outbox_event(notification_id=str(clone_notification.id))

            self._db.refresh(instance=clone_notification)
            self._db.commit()

            return NotificationResponse.model_validate(obj=clone_notification)
        except SQLAlchemyError as exc:
            self._db.rollback()
            logger.exception(msg="SQLAlchemyError Exception")

            raise DatabaseException() from exc

    def delete(self, user_owner_id: int, notification_id: int) -> NotificationResponse:
        try:
            statement = select(Notification).where(
                Notification.id == notification_id,
                Notification.status == NotificationStatus.FAILED,
                Notification.user_id == user_owner_id,
            )
            notification: Notification | None = self._db.scalar(statement=statement)
            if notification is None:
                logger.exception(
                    msg=f"The notification: {notification_id}, doesn't exists or isn't in the FAILED status"
                )
                raise NotificationMustFailedStatusException()

            notification.status = NotificationStatus.CANCELED
            self._db.commit()

            return NotificationResponse.model_validate(obj=notification)
        except SQLAlchemyError as exc:
            self._db.rollback()
            logger.exception(msg="SQLAlchemyError Exception")

            raise DatabaseException() from exc
