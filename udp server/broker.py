from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any

from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from nats.js.api import ConsumerConfig, DeliverPolicy, RetentionPolicy, StorageType, StreamConfig

LOG = logging.getLogger("topup.broker")


class DurableBroker:
    """NATS JetStream publisher: ACK is returned only after disk-backed publish."""

    def __init__(self, url: str, stream: str, subject: str) -> None:
        self.url = url
        self.stream = stream
        self.subject = subject
        self.nc = NATS()
        self.js: JetStreamContext | None = None

    async def connect(self) -> None:
        await self.nc.connect(self.url, name="topup-udp-ingress")
        self.js = self.nc.jetstream()
        try:
            await self.js.stream_info(self.stream)
        except Exception:
            await self.js.add_stream(
                StreamConfig(
                    name=self.stream,
                    subjects=[self.subject, f"{self.subject}.dlq"],
                    retention=RetentionPolicy.LIMITS,
                    storage=StorageType.FILE,
                    max_msgs=-1,
                    max_age=0,
                )
            )
        LOG.info("NATS JetStream connected stream=%s subject=%s", self.stream, self.subject)

    async def publish(self, packet_id: str, payload: bytes, address: tuple[str, int], received_at: float) -> None:
        if self.js is None:
            raise RuntimeError("broker is not connected")
        body = json.dumps(
            {
                "packet_id": packet_id,
                "payload": payload.hex(),
                "client_ip": address[0],
                "client_port": address[1],
                "received_at": received_at,
            },
            separators=(",", ":"),
        ).encode()
        # JetStream PubAck means the message is accepted by the stream's file store.
        await self.js.publish(self.subject, body, headers={"Nats-Msg-Id": packet_id})

    async def close(self) -> None:
        if self.nc.is_connected:
            await self.nc.drain()


async def ensure_consumer(js: JetStreamContext, stream: str, durable: str, subject: str) -> None:
    try:
        await js.consumer_info(stream, durable)
    except Exception:
        await js.add_consumer(
            stream,
            ConsumerConfig(
                durable_name=durable,
                filter_subject=subject,
                deliver_policy=DeliverPolicy.ALL,
                ack_wait=30,
                max_deliver=5,
            ),
        )
