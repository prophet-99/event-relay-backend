import json
from dataclasses import asdict

from botocore.client import BaseClient

from app.outbox_events.messaging.event_envelope import OutboxEventEnvelope


class SQSOutboxEventPublisher:
    def __init__(self, sqs_client: BaseClient, queue_url: str) -> None:
        self._sqs_client = sqs_client
        self._queue_url = queue_url

    def publish(self, event: OutboxEventEnvelope) -> None:
        message_body = json.dumps(asdict(event))

        self._sqs_client.send_message(
            QueueUrl=self._queue_url, MessageBody=message_body
        )
