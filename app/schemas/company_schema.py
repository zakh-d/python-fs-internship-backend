from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user_shema import UserSchema


class CompanySchema(BaseModel):

    id: UUID
    name: Annotated[str, Field(max_length=49)]
    description: Annotated[str, Field(max_length=249)]
    owner: UserSchema

    model_config = ConfigDict(from_attributes=True)


class CompanyListSchema(BaseModel):
    companies: list[CompanySchema]


class CompanyCreateSchema(BaseModel):
    name: Annotated[str, Field(max_length=49)]
    description: Annotated[str, Field(max_length=249)]
