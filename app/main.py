from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.health_check_router import router as health_check_router
from app.routers.users_router import router as users_router
from app.routers.company_router import router as company_router


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI()

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

    return app


app = create_app()
