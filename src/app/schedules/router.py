from fastapi import Query, status
from fastapi.routing import APIRouter

from app.schedules.schemas import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.schedules.service import ScheduleService

router = APIRouter(prefix="/schedule")
schedule_service = ScheduleService()


@router.get(
    "/{schedule_id}", summary="Get schedule by id", response_model=ScheduleResponse
)
def get_schedule_by_id(schedule_id: str) -> ScheduleResponse:
    # return JSONResponse(
    #     status_code=status.HTTP_200_OK, content={"schedule_id": schedule_id}
    # )
    return schedule_service.get_by_id(schedule_id)


@router.get("/", summary="Get all schedules", response_model=list[ScheduleResponse])
def get_schedules(
    is_enabled: bool | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1),
) -> list[ScheduleResponse]:
    # return JSONResponse(
    #     status_code=status.HTTP_200_OK, content={"limit": limit, "is_active": is_active}
    # )
    return schedule_service.get_all(is_enabled=is_enabled, offset=offset, limit=limit)


@router.post(
    "/",
    summary="Create a schedule",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(schedule_request: ScheduleCreate) -> ScheduleResponse:
    return schedule_service.create(schedule_request)


@router.patch(
    "/{schedule_id}", summary="Update a schedule", response_model=ScheduleResponse
)
def update_schedule(
    schedule_id: str, schedule_request: ScheduleUpdate
) -> ScheduleResponse:
    return schedule_service.update(schedule_id, schedule_request)


@router.delete(
    "/{schedule_id}", summary="Delete a schedule", response_model=ScheduleResponse
)
def delete_schedule(
    schedule_id: str,
) -> ScheduleResponse:
    return schedule_service.delete(schedule_id)
