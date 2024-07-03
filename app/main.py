from fastapi import FastAPI

from app.schemas import HealthCheckInfo


app = FastAPI()


@app.get('/', description='Health check')
def get_root_status_checks() -> HealthCheckInfo:
    return HealthCheckInfo(
        status_code=200,
        details='ok',
        result='working'
    )
