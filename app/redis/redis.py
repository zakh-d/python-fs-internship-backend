import aioredis
from aioredis import Redis

from app.core.config import settings


async def get_redis_client() -> Redis:
    return await aioredis.from_url(settings.redis_url)
