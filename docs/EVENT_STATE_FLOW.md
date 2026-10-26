# State Flow: Notification and OutboxEvent

1. The API creates the `Notification` with the `PENDING` status.
2. Within the same transaction, the API creates an `OutboxEvent` with the
   `PENDING` status.
3. The publisher processes the `OutboxEvent` and publishes it to SQS:

   ```text
   PENDING → PUBLISHING → PUBLISHED
   ```

   During this step, the `Notification` remains `PENDING`.

4. SQS retains the message until a worker receives it. The `Notification`
   remains `PENDING`.
5. When the worker receives the message, it starts delivery through the
   appropriate channel —Email, SMS, or Push—:

   ```text
   Notification: PENDING → SENDING
   ```

6. The delivery result determines the final status or schedules the next
   retry:

   ```text
   SENDING → SENT
   SENDING → RETRY_SCHEDULED
   SENDING → FAILED
   ```
