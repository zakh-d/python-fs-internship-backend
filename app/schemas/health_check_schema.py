from pydantic import BaseModel


class HealthCheckInfo(BaseModel):
    status_code: int
    details: str
    result: str


class HealthCheckReport(BaseModel):
    app: HealthCheckInfo
    db: HealthCheckInfo
    redis: HealthCheckInfo
