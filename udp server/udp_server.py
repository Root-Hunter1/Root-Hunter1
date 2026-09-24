#!/usr/bin/env python3
"""UDP ingress that publishes durably before acknowledging the client.."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import socket
import time
import uuid
from dataclasses import dataclass

from broker import DurableBroker

LOG = logging.getLogger("topup.udp")


@dataclass(slots=True)
class Stats:
    received: int = 0
    acknowledged: int = 0
    dropped: int = 0
    invalid: int = 0
    errors: int = 0
    publish_retries: int = 0


class Protocol(asyncio.DatagramProtocol):
    def __init__(self, queue: asyncio.Queue[tuple[str, bytes, tuple[str, int], float]], stats: Stats, max_size: int):
        self.queue, self.stats, self.max_size = queue, stats, max_size
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]
        LOG.info("UDP transport ready")

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self.stats.received += 1
        if not data or len(data) > self.max_size:
            self.stats.invalid += 1
            return
        try:
            self.queue.put_nowait((str(uuid.uuid4()), bytes(data), addr, time.time()))
        except asyncio.QueueFull:
            self.stats.dropped += 1
            LOG.warning("input queue full; packet from %s was not accepted", addr)

    def error_received(self, exc: Exception) -> None:
        self.stats.errors += 1
        LOG.error("UDP error: %s", exc)


async def serve(args: argparse.Namespace) -> None:
    loop = asyncio.get_running_loop()
    stop = asyncio.Event()
    queue: asyncio.Queue[tuple[str, bytes, tuple[str, int], float]] = asyncio.Queue(args.queue_size)
    stats = Stats()
    broker = DurableBroker(args.nats_url, args.nats_stream, args.nats_subject)
    await broker.connect()

    protocol = Protocol(queue, stats, args.max_packet_size)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if args.reuse_port and hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.recv_buffer)
        sock.bind((args.host, args.port))
        transport, _ = await loop.create_datagram_endpoint(lambda: protocol, sock=sock)
    except Exception:
        sock.close()
        await broker.close()
        raise

    async def publisher() -> None:
        while True:
            packet_id, payload, addr, received_at = await queue.get()
            delay = 0.25
            try:
                while True:
                    try:
                        await broker.publish(packet_id, payload, addr, received_at)
                        break
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        stats.errors += 1
                        stats.publish_retries += 1
                        LOG.exception("durable publish failed; retrying in %.2fs", delay)
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, args.retry_max_delay)

                if protocol.transport is not None:
                    protocol.transport.sendto(b"OK " + packet_id.encode(), addr)
                stats.acknowledged += 1
            finally:
                queue.task_done()

    task = asyncio.create_task(publisher())
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            LOG.warning("signal handler unavailable for %s", sig)
    LOG.info("listening on %s:%d", args.host, args.port)
    try:
        await stop.wait()
        transport.close()
        await asyncio.wait_for(queue.join(), args.shutdown_timeout)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        transport.close()
        await broker.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=os.getenv("UDP_HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.getenv("UDP_PORT", "9999")))
    p.add_argument("--queue-size", type=int, default=50000)
    p.add_argument("--max-packet-size", type=int, default=1400)
    p.add_argument("--recv-buffer", type=int, default=4 * 1024 * 1024)
    p.add_argument("--shutdown-timeout", type=float, default=30)
    p.add_argument("--retry-max-delay", type=float, default=30)
    p.add_argument("--nats-url", default=os.getenv("NATS_URL", "nats://127.0.0.1:4222"))
    p.add_argument("--nats-stream", default=os.getenv("NATS_STREAM", "TOPUP_EVENTS"))
    p.add_argument("--nats-subject", default=os.getenv("NATS_SUBJECT", "topup.events"))
    p.add_argument("--reuse-port", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(serve(parse_args()))
