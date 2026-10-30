from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class NotificationMessage:
    destination: str
    payload: dict[str, Any]
    user_id: int
    sent_at: datetime
    message: str
