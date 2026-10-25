from dataclasses import dataclass

import boto3
from botocore.client import BaseClient


@dataclass(frozen=True)
class SQSClientConfig:
    region_name: str
    endpoint_url: str | None = None


def create_sqs_client(config: SQSClientConfig) -> BaseClient:
    return boto3.client(
        "sqs", region_name=config.region_name, endpoint_url=config.endpoint_url
    )
