from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.db import async_session
from app.routers.company_router import router as company_router
from app.routers.health_check_router import router as health_check_router
from app.routers.notification_router import router as notification_router
from app.routers.quizz_router import router as quizz_router
from app.routers.users_router import router as users_router
from app.utils.scheduler import check_quizz_completions


@asynccontextmanager
async def start_quizz_scheduler(app: FastAPI) -> AsyncGenerator[None, None]:
    async with async_session() as session:
        scheduler = AsyncIOScheduler()
        midnight_trigger = CronTrigger(second=0, minute=0, hour=0, day='*', month='*', year='*')
        task = scheduler.add_job(
            check_quizz_completions, args=[session], trigger=midnight_trigger, replace_existing=True
        )
        scheduler.start()
        yield
        task.remove()
        scheduler.shutdown()


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(lifespan=start_quizz_scheduler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(health_check_router, prefix='/health', tags=['health'])
    app.include_router(users_router, prefix='/users', tags=['users'])
    app.include_router(company_router, prefix='/companies', tags=['companies'])
    app.include_router(quizz_router, prefix='/quizzes', tags=['quizzes'])
    app.include_router(notification_router, prefix='/notifications', tags=['notifications'])

    return app


app = create_app()
