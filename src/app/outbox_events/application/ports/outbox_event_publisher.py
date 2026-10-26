from typing import Protocol

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope


class OutboxEventPublisher(Protocol):
    def publish(self, event: OutboxEventEnvelope) -> None: ...
