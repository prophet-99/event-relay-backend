from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScheduleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    run_at: datetime
    is_enabled: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(ScheduleBase):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    run_at: Optional[datetime] = None  # Old type method
    is_enabled: bool = False


class ScheduleResponse(ScheduleBase):
    id: str
