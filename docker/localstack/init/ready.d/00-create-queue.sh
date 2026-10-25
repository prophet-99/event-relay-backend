#!/usr/bin/env bash
set -euo pipefail

awslocal sqs create-queue \
  --queue-name "$SQS_QUEUE_NAME" \
  --region "$DEFAULT_REGION"
