import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import get_db
from app.schemas import HealthCheckReport, HealthCheckInfo
from app.services.health_check_service import check_db_health, check_redis_health


logger = logging.getLogger(__name__)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', description='Health check')
async def get_root_status_checks(db: AsyncSession = Depends(get_db)) -> HealthCheckReport:
    app_health_check = HealthCheckInfo(
        status_code=200,
        details='App is healthy',
        result='working'
    ) # app is always healthy if we can reach this point

    db_health_check = await check_db_health(db)
    redis_health_check = await check_redis_health()

    return HealthCheckReport(
        app=app_health_check,
        db=db_health_check,
        redis=redis_health_check
    )
