from app.db.database import SessionLocal
from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.application.services.outbox_publishing_service import (
    OutboxPublishingService,
)
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_publisher import (
    SQSOutboxEventPublisher,
)
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.settings.app_settings import get_app_settings


def main():
    app_settings = get_app_settings()

    sqs_client = create_sqs_client(
        config=SQSClientConfig(
            region_name=app_settings.aws_region,
            endpoint_url=app_settings.sqs_endpoint_url,
        )
    )

    sqs_publisher: OutboxEventPublisher = SQSOutboxEventPublisher(
        sqs_client=sqs_client, queue_url=app_settings.sqs_queue_url
    )

    with SessionLocal() as db_session:
        outbox_publishing_service = OutboxPublishingService(
            db_session=db_session, publisher=sqs_publisher
        )
        outbox_publishing_service.publish_next_pending_event()


if __name__ == "__main__":
    main()
