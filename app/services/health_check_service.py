from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.redis import get_redis_client
from app.schemas.health_check_schema import HealthCheckInfo
from app.utils.logging import logger


async def check_redis_health() -> HealthCheckInfo:
    redis_client = await get_redis_client()

    try:
        await redis_client.ping()
        return HealthCheckInfo(status_code=200, details='Redis is healthy', result='working')
    except Exception:
        logger.error('Redis is down')
        return HealthCheckInfo(status_code=500, details='Redis in down', result='FAIL')


async def check_db_health(db: AsyncSession) -> HealthCheckInfo:
    try:
        await db.execute(text('SELECT 1'))
        return HealthCheckInfo(status_code=200, details='Database is healthy', result='working')
    except Exception:
        logger.error('Database is down')
        return HealthCheckInfo(status_code=500, details='Database is down', result='FAIL')
