from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import HealthCheckInfo
from app.utils.config import Config

app = FastAPI()
config = Config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config['ALLOWED_HOSTS'],
    allow_credentials=True,
    allow_methods=config['ALLOWED_METHODS'],
    allow_headers=config['ALLOWED_HEADERS'],
)


@app.get('/', description='Health check')
def get_root_status_checks() -> HealthCheckInfo:
    return HealthCheckInfo(
        status_code=200,
        details='ok',
        result='working'
    )
