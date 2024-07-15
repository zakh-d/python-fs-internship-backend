import aioredis
from aioredis import Redis
from app.core.config import settings


def get_redis_client() -> Redis:
    return aioredis.from_url(settings.redis_url)
