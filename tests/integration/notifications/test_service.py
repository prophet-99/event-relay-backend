from sqlalchemy.orm import Session

from app.notifications.constants import MAX_ATTEMPTS
from app.notifications.enums import NotificationChannel, NotificationStatus
from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate
from app.notifications.service import NotificationService
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
    assert notification_db.max_attempts == MAX_ATTEMPTS
    assert notification_db.user_id == existing_user.id
