#!/usr/bin/env python3
"""Durable JetStream consumer with atomic PostgreSQL writes and a DLQ."""
from __future__ import annotations

import asyncio
import json
import logging
import os

from nats.aio.client import Client as NATS
from database import Database
from broker import ensure_consumer

LOG = logging.getLogger("topup.consumer")
STREAM = os.getenv("NATS_STREAM", "TOPUP_EVENTS")
SUBJECT = os.getenv("NATS_SUBJECT", "topup.events")
DURABLE = os.getenv("NATS_DURABLE", "postgres-writer")
DLQ_SUBJECT = f"{SUBJECT}.dlq"
MAX_DELIVERIES = int(os.getenv("MAX_DELIVERIES", "5"))


async def send_to_dlq(js, msg, reason: str) -> None:
    # Publish first; acknowledge the source only after the DLQ publish succeeds.
    envelope = json.dumps(
        {"reason": reason, "original_subject": msg.subject, "payload": msg.data.decode("utf-8", "replace")},
        separators=(",", ":"),
    ).encode()
    await js.publish(DLQ_SUBJECT, envelope)
    await msg.ack()


async def run() -> None:
    nc = NATS()
    await nc.connect(os.getenv("NATS_URL", "nats://127.0.0.1:4222"), name="topup-postgres-consumer")
    js = nc.jetstream()
    await ensure_consumer(js, STREAM, DURABLE, SUBJECT)
    db = Database(os.environ["DATABASE_URL"], max_size=int(os.getenv("DB_POOL_SIZE", "10")))
    await db.connect()
    sub = await js.pull_subscribe(SUBJECT, durable=DURABLE, stream=STREAM)
    try:
        while True:
            try:
                messages = await sub.fetch(batch=int(os.getenv("BATCH_SIZE", "500")), timeout=1)
            except asyncio.TimeoutError:
                continue

            rows = []
            for msg in messages:
                try:
                    value = json.loads(msg.data)
                    rows.append({
                        "packet_id": value["packet_id"],
                        "payload": bytes.fromhex(value["payload"]),
                        "client_ip": value["client_ip"],
                        "client_port": int(value["client_port"]),
                        "received_at": float(value["received_at"]),
                        "_msg": msg,
                    })
                except Exception as exc:
                    try:
                        await send_to_dlq(js, msg, f"invalid_message: {exc}")
                    except Exception:
                        LOG.exception("could not publish malformed message to DLQ")

            if not rows:
                continue

            try:
                await db.save_events(rows)
            except Exception:
                LOG.exception("database batch failed")
                for row in rows:
                    msg = row["_msg"]
                    try:
                        metadata = msg.metadata
                        delivered = metadata.num_delivered if metadata else 1
                    except Exception:
                        delivered = 1
                    if delivered >= MAX_DELIVERIES:
                        try:
                            await send_to_dlq(js, msg, "database_retry_limit_exceeded")
                        except Exception:
                            LOG.exception("could not move message to DLQ")
                    else:
                        await msg.nak()
                continue

            for row in rows:
                await row["_msg"].ack()
    finally:
        await db.close()
        await nc.drain()


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    asyncio.run(run())
