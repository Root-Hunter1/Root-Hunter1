"""Async PostgreSQL integration for the UDP server..

The pool is shared by all UDP workers so database writes do not create a new
connection for every packet. Configure it with DATABASE_URL, for example:
postgresql://udp_user:udp_password@postgres:5432/udp_data
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from psycopg_pool import AsyncConnectionPool


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS udp_packets (
    id BIGSERIAL PRIMARY KEY,
    received_at TIMESTAMPTZ NOT NULL,
    sender_ip INET NOT NULL,
    sender_port INTEGER NOT NULL,
    raw_data BYTEA NOT NULL,
    processed_data BYTEA NOT NULL,
    latency_ms INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS udp_packets_received_at_idx
    ON udp_packets (received_at DESC);
"""

INSERT_PACKET_SQL = """
INSERT INTO udp_packets
    (received_at, sender_ip, sender_port, raw_data, processed_data, latency_ms)
VALUES (%s, %s, %s, %s, %s, %s)
"""


class Database:
    """Small async database adapter used by the UDP workers."""

    def __init__(self, dsn: Optional[str] = None, min_size: int = 1, max_size: int = 10):
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgresql://udp_user:udp_password@localhost:5432/udp_data",
        )
        self.pool = AsyncConnectionPool(
            conninfo=self.dsn,
            min_size=min_size,
            max_size=max_size,
            open=False,
        )

    async def connect(self) -> None:
        """Open the pool and create the packet table if necessary."""
        await self.pool.open()
        await self.pool.wait()
        async with self.pool.connection() as connection:
            await connection.execute(CREATE_TABLE_SQL)

    async def save_packet(
        self,
        raw_data: bytes,
        processed_data: bytes,
        address: tuple[str, int],
        received_at: float,
        latency_ms: int,
    ) -> None:
        sender_ip, sender_port = address[0], int(address[1])
        received_time = datetime.fromtimestamp(received_at, tz=timezone.utc)
        async with self.pool.connection() as connection:
            await connection.execute(
                INSERT_PACKET_SQL,
                (
                    received_time,
                    sender_ip,
                    sender_port,
                    raw_data,
                    processed_data,
                    latency_ms,
                ),
            )

    async def close(self) -> None:
        await self.pool.close()
~
~
~
~
~
~
~
~
~
~
~
~
~
