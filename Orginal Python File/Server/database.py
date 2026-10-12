import asyncpg


class Database:
    def __init__(self, dsn, max_size=4):
        self.dsn = dsn
        self.max_size = max_size
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.dsn, min_size=1, max_size=self.max_size
        )
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS packets (
                    id BIGSERIAL PRIMARY KEY,
                    ip TEXT,
                    port INTEGER,
                    payload BYTEA,
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)

    async def insert_many(self, rows):
        async with self.pool.acquire() as conn:
            await conn.copy_records_to_table(
                "packets", records=rows, columns=["ip", "port", "payload"]
            )

    async def close(self):
        if self.pool:
            await self.pool.close()
