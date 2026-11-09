from typing import Protocol, TypedDict

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope


class OutboxEventReceiveResponse(TypedDict):
    outbox_event_envelope: OutboxEventEnvelope
    receipt_handle: str


class OutboxEventConsumer(Protocol):
    def receive(self) -> OutboxEventReceiveResponse | None: ...
    def delete(self, receipt_handle: str) -> None: ...
