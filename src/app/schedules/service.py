from uuid import uuid4

from app.schedules.exceptions import ScheduleNotFoundException
from app.schedules.schemas import ScheduleCreate, ScheduleResponse, ScheduleUpdate


class ScheduleService:
    def __init__(self):
        self._schedules: dict[str, ScheduleResponse] = {}

    def get_by_id(self, schedule_id: str) -> ScheduleResponse:
        schedule_found = self._schedules.get(schedule_id)

        if schedule_found is None:
            raise ScheduleNotFoundException(schedule_id)
        return schedule_found

    def get_all(
        self, is_enabled: bool | None = None, offset: int = 0, limit: int = 10
    ) -> list[ScheduleResponse]:
        schedules = list(self._schedules.values())
        if is_enabled is not None:
            schedules = [
                schedule for schedule in schedules if schedule.is_enabled == is_enabled
            ]

        return schedules[offset : offset + limit]

    def create(self, schedule_request: ScheduleCreate) -> ScheduleResponse:
        schedule = ScheduleResponse(id=str(uuid4()), **schedule_request.model_dump())
        self._schedules[schedule.id] = schedule

        return schedule

    def update(
        self, schedule_id: str, schedule_request: ScheduleUpdate
    ) -> ScheduleResponse:
        schedule_found = self.get_by_id(schedule_id)

        schedule_db = schedule_found.model_dump()
        schedule_changes = schedule_request.model_dump(exclude_unset=True)
        schedule_db.update(schedule_changes)

        updated_schedule = ScheduleResponse(**schedule_db)
        self._schedules[schedule_id] = updated_schedule

        return updated_schedule

    def delete(self, schedule_id: str) -> ScheduleResponse:
        schedule_found = self.get_by_id(schedule_id)

        return self._schedules.pop(schedule_found.id)
