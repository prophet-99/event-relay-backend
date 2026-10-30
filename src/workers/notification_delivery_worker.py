from datetime import datetime, timezone
from typing import Any, TypedDict, cast

from pydantic import TypeAdapter
from sqlalchemy import CursorResult, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.notifications.application.dto.notification_message import NotificationMessage
from app.notifications.application.services.notification_publish_service import (
    NotificationPublishService,
)
from app.notifications.enums import NotificationStatus
from app.notifications.models import Notification
from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.settings.app_settings import get_app_settings


class SqsMessage(TypedDict):
    MessageId: str
    ReceiptHandle: str
    MD5OfBody: str
    Body: str


def run_listener_once(db_session: Session) -> None:
    app_settings = get_app_settings()
    sqs_client = create_sqs_client(
        config=SQSClientConfig(
            region_name=app_settings.aws_region,
            endpoint_url=app_settings.sqs_endpoint_url,
        )
    )

    sqs_response: dict[str, Any] = sqs_client.receive_message(
        QueueUrl=app_settings.sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=1,
    )
    sqs_messages: list[SqsMessage] = sqs_response.get("Messages", [])
    if len(sqs_messages) > 0:
        envelope_adapter = TypeAdapter(type=OutboxEventEnvelope)
        envelope_event: OutboxEventEnvelope = envelope_adapter.validate_json(
            sqs_messages[0]["Body"]
        )

        if (
            envelope_event.aggregate_type == "notification"
            and envelope_event.event_type == "notification.created"
        ):
            try:
                claim_statement = (
                    update(table=Notification)
                    .where(
                        Notification.id == envelope_event.aggregate_id,
                        Notification.status == NotificationStatus.PENDING,
                    )
                    .values(
                        status=NotificationStatus.SENDING,
                        attempt_count=Notification.attempt_count + 1,
                    )
                )
                result: CursorResult[Any] = cast(
                    typ=CursorResult[Any], val=db_session.execute(claim_statement)
                )
                if result.rowcount != 1:
                    db_session.rollback()
                    return
                db_session.commit()

                statement = select(Notification).where(
                    Notification.id == envelope_event.aggregate_id,
                )
                db_notification: Notification | None = db_session.scalar(
                    statement=statement
                )
                if db_notification is None:
                    db_session.rollback()
                    return

                # PROCESS WITH STRATEGY PATTERN
                sent_at = datetime.now(tz=timezone.utc)
                NotificationPublishService().publish_notification(
                    notification_channel=db_notification.channel,
                    notification_message=NotificationMessage(
                        destination=db_notification.destination,
                        message=db_notification.message,
                        payload=envelope_event.payload,
                        sent_at=sent_at,
                        user_id=db_notification.user_id,
                    ),
                )
                db_notification.status = NotificationStatus.SENT
                db_notification.sent_at = sent_at
                db_session.commit()

                sqs_client.delete_message(
                    QueueUrl=app_settings.sqs_queue_url,
                    ReceiptHandle=sqs_messages[0]["ReceiptHandle"],
                )
            except SQLAlchemyError:
                db_session.rollback()

        if envelope_event.event_type == "notification.deleted":
            # Not handled yet: do not claim or acknowledge the message.
            pass


if __name__ == "__main__":
    pass
    # run_listener_once()
