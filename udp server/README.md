# Durable UDP ingestion

```bash
pip install -r requirements.txt
docker compose up -d
export DATABASE_URL='postgresql://topup:topup@127.0.0.1:5432/topup'
python udp_server.py
```

In another terminal:

```bash
python event_consumer.py
```

The UDP server acknowledges a packet only after NATS JetStream returns a
publish acknowledgement. JetStream uses file storage, so the message survives
an application restart. The PostgreSQL consumer writes atomic, idempotent
batches and acknowledges NATS messages only after commit.

Database failures cause redelivery. After `MAX_DELIVERIES` attempts, the
consumer publishes the original message and reason to `topup.events.dlq`, then
acknowledges the source message. Malformed messages follow the same DLQ path.

This is durable across application crashes, but UDP itself cannot guarantee
that a packet reaches the server. Clients needing end-to-end delivery should
retry the same application transaction ID; use that ID as the JetStream
`Nats-Msg-Id` and PostgreSQL idempotency key.
