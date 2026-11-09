from typing import Any

from botocore.client import BaseClient
from pydantic import TypeAdapter

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope
from app.outbox_events.application.ports.outbox_event_consumer import (
    OutboxEventReceiveResponse,
)
from app.outbox_events.infrastructure.sqs.types.sqs_types import SQSMessageResponse


class SQSOutboxEventConsumer:
    def __init__(self, sqs_client: BaseClient, queue_url: str):
        self.sqs_client = sqs_client
        self.queue_url = queue_url

    def receive(self) -> OutboxEventReceiveResponse | None:
        sqs_response: dict[str, Any] = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )
        sqs_messages: list[SQSMessageResponse] = sqs_response.get("Messages", [])

        if len(sqs_messages) > 0:
            envelope_event: OutboxEventEnvelope = TypeAdapter(
                type=OutboxEventEnvelope
            ).validate_json(sqs_messages[0]["Body"])

            return {
                "outbox_event_envelope": envelope_event,
                "receipt_handle": sqs_messages[0]["ReceiptHandle"],
            }

        return None

    def delete(self, receipt_handle: str) -> None:
        self.sqs_client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
