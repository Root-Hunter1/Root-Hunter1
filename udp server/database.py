from __future__ import annotations

import logging
from typing import Any, Iterable

logger = logging.getLogger(__name__)


class Database:
    """Async PostgreSQL persistence with atomic, idempotent batch writes."""

    def __init__(self, url: str, max_size: int = 10) -> None:
        if not url:
            raise RuntimeError("DATABASE_URL is required")
        self.url = url
        self.max_size = max_size
        self.pool: Any = None

    async def connect(self) -> None:
        try:
            import asyncpg
        except ImportError as exc:
            raise RuntimeError("Install asyncpg: pip install asyncpg") from exc

        self.pool = await asyncpg.create_pool(
            self.url,
            min_size=1,
            max_size=self.max_size,
            command_timeout=10,
        )
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS udp_events (
                        packet_id UUID PRIMARY KEY,
                        payload BYTEA NOT NULL,
                        client_ip INET NOT NULL,
                        client_port INTEGER NOT NULL CHECK (client_port BETWEEN 0 AND 65535),
                        received_at TIMESTAMPTZ NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
        except Exception:
            await self.close()
            raise
        logger.info("PostgreSQL connected and schema is ready")

    async def save_events(self, events: Iterable[dict[str, Any]]) -> int:
        if self.pool is None:
            raise RuntimeError("database pool is not connected")

        rows = [
            (
                event["packet_id"],
                event["payload"],
                event["client_ip"],
                event["client_port"],
                event["received_at"],
            )
            for event in events
        ]
        if not rows:
            return 0

        # The transaction is atomic. Retrying the same batch is safe because
        # packet_id is the idempotency key.
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(
                    """
                    INSERT INTO udp_events
                        (packet_id, payload, client_ip, client_port, received_at)
                    VALUES ($1, $2, $3, $4, to_timestamp($5))
                    ON CONFLICT (packet_id) DO NOTHING
                    """,
                    rows,
                )
        return len(rows)

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
