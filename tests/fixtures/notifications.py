import pytest
from sqlalchemy.orm import Session

from app.notifications.enums import NotificationChannel, NotificationStatus
from app.notifications.models import Notification
from app.users.models import User


@pytest.fixture
def existing_notification(db_session: Session, existing_user: User) -> Notification:
    new_notification = Notification(
        title="Test notification",
        message="This is a manual test notification.",
        channel=NotificationChannel.EMAIL,
        destination="recipient@example.com",
        status=NotificationStatus.PENDING,
        max_attempts=3,
        attempt_count=0,
        user_id=existing_user.id,
    )

    db_session.add(instance=new_notification)
    db_session.flush()

    return new_notification
