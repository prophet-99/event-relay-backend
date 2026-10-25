from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OutboxEventEnvelope:
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    payload: dict[str, Any]
