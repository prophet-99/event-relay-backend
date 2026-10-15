from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.notifications.constants import MAX_SEND_ATTEMPTS
from app.notifications.enums import NotificationChannel, NotificationStatus
from app.notifications.exceptions import DatabaseException
from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate
from app.notifications.service import NotificationService
from app.outbox_events.constants import MAX_PUBLISH_ATTEMPTS
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent
from app.users.models import User


def test_create_notification(db_session: Session, existing_user: User) -> None:
    # Arrange
    notification_service = NotificationService(db_session)
    notification_request = NotificationCreate(
        title="Notificación de prueba",
        message="Esta es una prueba de notificación",
        channel=NotificationChannel.EMAIL,
        destination="test@gmail.com",
    )
    # Act
    notification_response = notification_service.create(
        notification_request=notification_request, user_owner_id=existing_user.id
    )
    # Assert
    assert notification_response.id >= 0

    assert notification_response.title == notification_request.title
    assert notification_response.message == notification_request.message
    assert notification_response.channel == notification_request.channel
    assert notification_response.destination == notification_request.destination

    assert notification_response.status == NotificationStatus.PENDING

    notification_db = db_session.get(Notification, notification_response.id)
    assert notification_db is not None
    assert notification_db.max_attempts == MAX_SEND_ATTEMPTS
    assert notification_db.user_id == existing_user.id

    statement = select(OutboxEvent).where(
        OutboxEvent.aggregate_id == str(notification_db.id)
    )
    outbox_event_db = db_session.scalars(statement).one_or_none()
    assert outbox_event_db is not None
    assert outbox_event_db.status == OutboxEventStatus.PENDING
    assert outbox_event_db.max_publish_attempts == MAX_PUBLISH_ATTEMPTS
    assert outbox_event_db.payload == {}
    assert outbox_event_db.aggregate_type == "notification"
    assert outbox_event_db.event_type == "notification.created"


def test_create_notification_with_outbox_event_rollback(
    db_session: Session,
    existing_isolated_outbox_event: OutboxEvent,
    existing_user: User,
) -> None:
    # Arrange
    notification_service = NotificationService(db_session)
    notification_request = NotificationCreate(
        title="Notificación de prueba",
        message="Esta es una prueba de notificación",
        channel=NotificationChannel.EMAIL,
        destination="test@gmail.com",
    )

    # Act
    with patch(
        "app.notifications.service.uuid4",
        return_value=existing_isolated_outbox_event.event_id,
    ) as uuid4_spy:
        # Arrange
        # Act
        with pytest.raises(DatabaseException):
            notification_service.create(
                notification_request=notification_request,
                user_owner_id=existing_user.id,
            )

        # Assert
        uuid4_spy.assert_called_once()

    # Assert
    outbox_events_statement = select(OutboxEvent)
    outbox_events = db_session.scalars(outbox_events_statement).all()
    assert len(outbox_events) == 0

    notification_statement = select(Notification)
    notifications = db_session.scalars(notification_statement).all()
    assert len(notifications) == 0
