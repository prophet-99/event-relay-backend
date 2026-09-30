from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schedules.exceptions import (
    DatabaseOperationException,
    ScheduleNotFoundException,
)
from app.schedules.models import Schedule
from app.schedules.schemas import ScheduleCreate, ScheduleResponse, ScheduleUpdate


class ScheduleService:
    def __init__(self, db: Session):
        self._db = db

    def _get_schedule_or_raise(self, schedule_id: str) -> Schedule:
        schedule_found = self._db.get(Schedule, schedule_id)
        if schedule_found is None:
            raise ScheduleNotFoundException(schedule_id)

        return schedule_found

    def _commit_or_raise(self) -> None:
        try:
            self._db.commit()
        except SQLAlchemyError as exc:
            self._db.rollback()

            raise DatabaseOperationException from exc

    def get_by_id(self, schedule_id: str) -> ScheduleResponse:
        schedule_found = self._get_schedule_or_raise(schedule_id)

        return ScheduleResponse.model_validate(schedule_found)

    def get_all(
        self, is_enabled: bool | None = None, offset: int = 0, limit: int = 10
    ) -> list[ScheduleResponse]:
        statement = select(Schedule)

        if is_enabled is not None:
            statement = statement.where(Schedule.is_enabled == is_enabled)

        statement = statement.order_by(Schedule.name.asc(), Schedule.id.asc())
        statement = statement.offset(offset).limit(limit)
        schedules = self._db.scalars(statement).all()

        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    def create(self, schedule_request: ScheduleCreate) -> ScheduleResponse:
        new_schedule = Schedule(id=str(uuid4()), **schedule_request.model_dump())

        self._db.add(new_schedule)
        self._commit_or_raise()

        return ScheduleResponse.model_validate(new_schedule)

    def update(
        self, schedule_id: str, schedule_request: ScheduleUpdate
    ) -> ScheduleResponse:
        schedule_to_update = self._get_schedule_or_raise(schedule_id)
        schedule_changes = schedule_request.model_dump(exclude_unset=True)
        for key, value in schedule_changes.items():
            setattr(schedule_to_update, key, value)

        self._commit_or_raise()

        return ScheduleResponse.model_validate(schedule_to_update)

    def delete(self, schedule_id: str) -> ScheduleResponse:
        schedule_to_delete = self._get_schedule_or_raise(schedule_id)
        deleted_schedule = ScheduleResponse.model_validate(schedule_to_delete)

        self._db.delete(schedule_to_delete)
        self._commit_or_raise()

        return deleted_schedule
