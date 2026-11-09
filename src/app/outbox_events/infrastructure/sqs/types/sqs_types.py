from typing import TypedDict


class SQSMessageResponse(TypedDict):
    MessageId: str
    ReceiptHandle: str
    MD5OfBody: str
    Body: str
