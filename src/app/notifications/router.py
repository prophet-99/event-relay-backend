from datetime import datetime

from fastapi import APIRouter

from app.notifications.dependencies import NotificationServiceDep
from app.notifications.schemas import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/notification", tags=["Notification Module"])


@router.get(
    path="/",
    summary="Get all notifications for the current user an date range",
    response_model=list[NotificationResponse],
)
def get_by_range(
    notification_service: NotificationServiceDep,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[NotificationResponse]:
    return notification_service.get_by_range(
        user_owner_id=2, start_date=start_date, end_date=end_date
    )


@router.post(
    path="/",
    summary="Create a new notification for the current user",
    response_model=NotificationResponse,
)
def create(
    notification_service: NotificationServiceDep,
    notification_request: NotificationCreate,
) -> NotificationResponse:
    return notification_service.create(
        user_owner_id=2, notification_request=notification_request
    )


@router.put(
    path="/{notification_id}",
    summary="Update a new notification for the current user",
    response_model=NotificationResponse,
)
def update(
    notification_service: NotificationServiceDep,
    notification_id: int,
    notification_request: NotificationCreate,
) -> NotificationResponse:
    return notification_service.clone_from_parent(
        notification_id=notification_id,
        user_owner_id=2,
        notification_request=notification_request,
    )


@router.delete(
    path="/{notification_id}",
    summary="Delete a notification for the current user",
    response_model=NotificationResponse,
)
def delete(
    notification_service: NotificationServiceDep,
    notification_id: int,
) -> NotificationResponse:
    return notification_service.delete(user_owner_id=2, notification_id=notification_id)
