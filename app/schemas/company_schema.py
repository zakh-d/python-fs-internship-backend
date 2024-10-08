from typing import Annotated, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user_shema import UserSchema


class CompanySchema(BaseModel):
    id: UUID
    name: Annotated[str, Field(max_length=49)]
    description: Annotated[str, Field(max_length=249)]
    owner: UserSchema

    model_config = ConfigDict(from_attributes=True)


class CompanyDetailSchema(CompanySchema):
    hidden: bool


class CompanyDetailWithIsMemberSchema(CompanyDetailSchema):
    is_member: Literal['yes', 'no', 'pending_request', 'pending_invite']


class CompanyListSchema(BaseModel):
    companies: list[CompanySchema]
    total_count: int


class CompanyCreateSchema(BaseModel):
    name: Annotated[str, Field(max_length=49)]
    description: Annotated[str, Field(max_length=249)]
    hidden: bool


class CompanyUpdateSchema(BaseModel):
    name: Optional[Annotated[str, Field(max_length=49)]] = None
    description: Optional[Annotated[str, Field(max_length=249)]] = None
    hidden: Optional[bool] = None
