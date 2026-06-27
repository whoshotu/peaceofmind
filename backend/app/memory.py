import os
import asyncpg

class MemoryStore:
    def __init__(self):
        self.dsn = os.getenv("POSTGRES_DSN", "postgresql://user:pass@localhost:5432/peaceofmind")
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def set(self, user_id: str, key: str, value: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO memories (user_id, key, value, updated_at) VALUES ($1, $2, $3, now()) "
                "ON CONFLICT (user_id, key) DO UPDATE SET value = $3, updated_at = now()",
                user_id, key, value,
            )

    async def get(self, user_id: str, key: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT value FROM memories WHERE user_id = $1 AND key = $2",
                user_id, key,
            )
            return row["value"] if row else None

    async def delete_old(self, max_age_seconds: int = 86400):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM memories WHERE updated_at < now() - interval '${max_age_seconds} seconds'"
            )
