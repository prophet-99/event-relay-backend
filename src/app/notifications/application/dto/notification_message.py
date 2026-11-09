from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NotificationMessage:
    destination: str
    payload: dict[str, Any]
    user_id: int
    message: str
