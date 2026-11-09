from typing import Protocol

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope


class EventHandler(Protocol):
    def handle(self, outbox_event_dto: OutboxEventEnvelope) -> None: ...
