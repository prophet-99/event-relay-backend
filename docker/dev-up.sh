#!/usr/bin/env bash
set -euo pipefail

read_env_value() {
  local key="$1"

  awk -F= -v key="$key" '
    { sub(/\r$/, "") }
    $1 == key { print $2; exit }
  ' .env
}

readonly MAX_ATTEMPTS=30
SQS_QUEUE_NAME="$(read_env_value "SQS_QUEUE_NAME")"
AWS_REGION="$(read_env_value "AWS_REGION")"

docker compose --env-file .env -f docker-compose-dev.yml up -d

SQS_QUEUE_URL=""

for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
  if SQS_QUEUE_URL="$(
    docker compose --env-file .env -f docker-compose-dev.yml exec -T localstack \
    awslocal sqs get-queue-url --queue-name "$SQS_QUEUE_NAME" --region "$AWS_REGION" \
    --query "QueueUrl" --output text 2>/dev/null
  )"; then
    break
  fi

  sleep 1
done

if [[ -z "$SQS_QUEUE_URL" ]]; then
  echo "[x] Error: LocalStack queue was not ready after ${MAX_ATTEMPTS} seconds." >&2
  exit 1
fi

temporary_file="$(mktemp ".env.tmp.XXXXXX")"

awk -v queue_url="$SQS_QUEUE_URL" '
  { sub(/\r$/, "") }

  /^SQS_QUEUE_URL=/ {
    print "SQS_QUEUE_URL=" queue_url
    next
  }

  { print }
' .env > "$temporary_file"

mv "$temporary_file" .env

printf "LocalStack ready.\n"
printf "Queue: %s\n" "$SQS_QUEUE_NAME"
printf "SQS_QUEUE_URL updated in .env.\n"
