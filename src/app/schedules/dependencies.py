from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schedules.service import ScheduleService


def get_schedule_service(_db: Annotated[Session, Depends(get_db)]) -> ScheduleService:
    return ScheduleService(_db)


ScheduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]
