from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.schemas.health_check_schema import HealthCheckInfo, HealthCheckReport
from app.services.health_check_service import check_db_health, check_redis_health

router = APIRouter()


@router.get('/', description='Complete health check')
async def get_root_status_checks(db: Annotated[AsyncSession, Depends(get_db)]) -> HealthCheckReport:
    app_health_check = HealthCheckInfo(
        status_code=200, details='App is healthy', result='working'
    )  # app is always healthy if we can reach this point

    db_health_check = await check_db_health(db)
    redis_health_check = await check_redis_health()

    return HealthCheckReport(app=app_health_check, db=db_health_check, redis=redis_health_check)


@router.get('/app', description='App health check')
async def get_app_health() -> HealthCheckInfo:
    return HealthCheckInfo(status_code=200, details='App is healthy since we can reach this point.', result='working')


@router.get('/redis', description='Redis health check')
async def get_redis_health() -> HealthCheckInfo:
    return await check_redis_health()


@router.get('/db', description='Database health check')
async def get_db_health(db: Annotated[AsyncSession, Depends(get_db)]) -> HealthCheckInfo:
    return await check_db_health(db)
