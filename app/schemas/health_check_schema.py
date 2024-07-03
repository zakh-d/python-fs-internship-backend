from pydantic import BaseModel


class HealthCheckInfo(BaseModel):
    status_code: int
    details: str
    result: str
