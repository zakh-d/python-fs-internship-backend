import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db, redis_client
from app.schemas import HealthCheckInfo
from app.core.config import settings


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info('Database initialized')

    await redis_client.ping()
    logger.info('Pinged redis')
    yield

    await redis_client.aclose()
    logger.info('Closed redis connection')


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', description='Health check')
async def get_root_status_checks() -> HealthCheckInfo:
    return HealthCheckInfo(
        status_code=200,
        details='ok',
        result='working'
    )
