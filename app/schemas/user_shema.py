from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime


class UserSignInSchema(BaseModel):
    username: str
    password: str


class UserSignUpSchema(UserSignInSchema):
    email: str
    password_confirmation: str


class UserUpdateSchema(BaseModel):
    username: str
    email: str
    password: str  # password needed to cofirm user intentions


class UserDetail(UserSchema):
    pass


class UserList(BaseModel):
    users: list[UserSchema] = []
