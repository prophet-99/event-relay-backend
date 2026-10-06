from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


def validate_user_is_at_least_18(birthday_date: date) -> date:
    today: date = datetime.now(tz=timezone.utc).date()
    age = today.year - birthday_date.year
    has_not_had_birthday = (today.month, today.day) < (
        birthday_date.month,
        birthday_date.day,
    )

    if has_not_had_birthday:
        age -= 1
    if age < 18:
        raise ValueError("User must be at least 18 years old.")

    return birthday_date


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=100)
    birthday_date: date
    email: str = Field(max_length=254)
    is_enabled: bool = True


class UserCreate(UserBase):
    @field_validator("birthday_date", mode="after")
    @classmethod
    def ensure_user_is_adult(cls, birthday_date: date) -> date:
        return validate_user_is_at_least_18(birthday_date)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    birthday_date: date | None = None
    email: str | None = Field(default=None, max_length=254)

    @field_validator("name", "last_name", "birthday_date", "email", mode="before")
    @classmethod
    def validate_if_none(cls, value: object, info: ValidationInfo) -> object:
        if value is None:
            raise ValueError(f"The field {info.field_name} can't be null")

        return value

    @field_validator("birthday_date", mode="after")
    @classmethod
    def ensure_user_is_adult(cls, birthday_date: date) -> date:
        return validate_user_is_at_least_18(birthday_date)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    last_name: str
