from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import HealthCheckInfo
from app.core.config import settings

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', description='Health check')
def get_root_status_checks() -> HealthCheckInfo:
    return HealthCheckInfo(
        status_code=200,
        details='ok',
        result='working'
    )
