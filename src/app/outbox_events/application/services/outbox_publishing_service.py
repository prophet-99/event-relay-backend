from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope
from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent


class OutboxPublishingService:
    def __init__(self, db_session: Session, publisher: OutboxEventPublisher) -> None:
        self._db_session = db_session
        self._publisher = publisher

    def publish_next_pending_event(self) -> None:
        statement = (
            select(OutboxEvent)
            .order_by(OutboxEvent.created_at.asc())
            .where(OutboxEvent.status == OutboxEventStatus.PENDING)
            .limit(1)
        )
        pending_outbox_event = self._db_session.scalar(statement)

        if pending_outbox_event is not None:
            claim_statement = (
                update(OutboxEvent)
                .where(
                    OutboxEvent.id == pending_outbox_event.id,
                    OutboxEvent.status == OutboxEventStatus.PENDING,
                )
                .values(
                    status=OutboxEventStatus.PUBLISHING,
                    publish_attempt_count=OutboxEvent.publish_attempt_count + 1,
                )
            )
            result = cast(
                typ=CursorResult[Any], val=self._db_session.execute(claim_statement)
            )
            if result.rowcount != 1:
                self._db_session.rollback()
                return
            self._db_session.commit()

            publishing_outbox_event = pending_outbox_event
            outbox_event_envelope_dto = OutboxEventEnvelope(
                aggregate_id=publishing_outbox_event.aggregate_id,
                aggregate_type=publishing_outbox_event.aggregate_type,
                event_id=publishing_outbox_event.event_id,
                event_type=publishing_outbox_event.event_type,
                payload=publishing_outbox_event.payload,
            )
            self._publisher.publish(event=outbox_event_envelope_dto)

            publishing_outbox_event.status = OutboxEventStatus.PUBLISHED
            publishing_outbox_event.published_at = datetime.now(tz=timezone.utc)
            self._db_session.commit()
