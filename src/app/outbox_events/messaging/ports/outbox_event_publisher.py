from typing import Protocol

from app.outbox_events.messaging.event_envelope import OutboxEventEnvelope


class OutboxEventPublisher(Protocol):
    def publish(self, event: OutboxEventEnvelope) -> None: ...
