from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from app.users.models import User


class AccessTokenPayload(BaseModel):
    sub: str
    exp: int


@dataclass(frozen=True, slots=True)
class AuthenticationSecurity:
    user: User
    expires_at: datetime
