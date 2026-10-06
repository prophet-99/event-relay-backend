from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.users.schemas import UserSummary


class ScheduleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    run_at: datetime
    is_enabled: bool = True


class ScheduleCreate(ScheduleBase):
    user_id: int


class ScheduleUpdate(ScheduleBase):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    run_at: Optional[datetime] = None  # Old type method
    is_enabled: bool | None = None

    @field_validator("name", "run_at", "is_enabled", mode="before")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("This fied can't be null")

        return value


class ScheduleResponse(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user: UserSummary
