from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models import CompanyActionType


class CompanyActionCreateSchema(BaseModel):
    user_id: UUID
    company_id: UUID


class CompanyActionSchema(CompanyActionCreateSchema):
    type: CompanyActionType

    model_config = ConfigDict(from_attributes=True)
