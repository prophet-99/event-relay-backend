from logging import getLogger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.notifications.constants import MAX_ATTEMPTS
from app.notifications.enums import NotificationStatus
from app.notifications.exceptions import DatabaseException
from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate, NotificationResponse

logger = getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self._db = db

    def _commit_or_raise(self) -> None:
        try:
            self._db.commit()
        except SQLAlchemyError:
            self._db.rollback()

            raise

    def create(
        self, notification_request: NotificationCreate, user_owner_id: int
    ) -> NotificationResponse:
        new_notification = Notification(
            **notification_request.model_dump(),
            status=NotificationStatus.PENDING,
            max_attempts=MAX_ATTEMPTS,
            user_id=user_owner_id,
        )

        try:
            self._db.add(new_notification)
            self._commit_or_raise()
            self._db.refresh(new_notification)

            return NotificationResponse.model_validate(new_notification)
        except SQLAlchemyError as exc:
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseException() from exc
