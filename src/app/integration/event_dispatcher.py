from app.integration.event_handler import EventHandler
from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope


class EventDispatcher:
    def __init__(self, handlers: dict[str, EventHandler]) -> None:
        self.handlers = handlers

    def dispatch(self, outbox_event_dto: OutboxEventEnvelope) -> None:
        search_key = f"{outbox_event_dto.event_type}-{outbox_event_dto.aggregate_type}"
        self.handlers[search_key].handle(outbox_event_dto=outbox_event_dto)
