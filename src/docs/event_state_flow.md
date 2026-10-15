# Flujo de estados: Notification y OutboxEvent

1. La API crea la `Notification` con estado `PENDING`.
2. En la misma transacción, la API crea un `OutboxEvent` con estado `PENDING`.
3. El publisher procesa el `OutboxEvent` y lo publica en SQS:

   ```text
   PENDING → PUBLISHING → PUBLISHED
   ```

   Durante este paso, la `Notification` permanece en `PENDING`.

4. SQS conserva el mensaje hasta que un worker lo reciba. La `Notification`
   sigue en `PENDING`.
5. Cuando el worker recibe el mensaje, inicia el envío por el canal
   correspondiente —Email, SMS o Push—:

   ```text
   Notification: PENDING → SENDING
   ```

6. El resultado del envío determina el estado final o el siguiente reintento:

   ```text
   SENDING → SENT
   SENDING → RETRY_SCHEDULED
   SENDING → FAILED
   ```
