from datetime import datetime
from typing import Annotated, Self
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, model_validator


class UserSchema(BaseModel):
    id: UUID
    username: Annotated[str, Field(min_length=3, max_length=49)]
    email: Annotated[EmailStr, Field(max_length=49)]
    created_at: datetime
    updated_at: datetime


class UserSignInSchema(BaseModel):
    username: str
    password: Annotated[str, Field(max_length=255)]


class UserSignUpSchema(UserSignInSchema):
    email: Annotated[EmailStr, Field(max_length=49)]
    password_confirmation: str  # can be of any length bc never will be hashed or stored in db

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password_confirmation
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self


class UserUpdateSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=49)]
    email: Annotated[EmailStr, Field(max_length=49)]
    password: Annotated[str, Field(max_length=255)]  # password needed to cofirm user intentions


class UserDetail(UserSchema):
    pass


class UserList(BaseModel):
    users: list[UserSchema] = []
