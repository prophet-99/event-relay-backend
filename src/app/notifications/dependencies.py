from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.notifications.application.services.notification_service import (
    NotificationService,
)


def get_notification_service(
    db_session: Annotated[Session, Depends(dependency=get_db)],
) -> NotificationService:
    return NotificationService(db=db_session)


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
