from datetime import datetime
from typing import Annotated, Optional, Union
from typing_extensions import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserSchema(BaseModel):
    id: UUID
    username: Annotated[str, Field(min_length=3, max_length=49)]
    email: Annotated[EmailStr, Field(max_length=49)]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSignInSchema(BaseModel):
    email: Annotated[EmailStr, Field(max_length=49)]
    password: Annotated[str, Field(max_length=255)]


class UserSignUpSchema(UserSignInSchema):
    username: Annotated[str, Field(min_length=3, max_length=49)]
    first_name: Annotated[str, Field(max_length=49)]
    last_name: Annotated[str, Field(max_length=49)]
    password: Annotated[str, Field(min_length=8, max_length=255)]
    password_confirmation: str  # can be of any length bc never will be hashed or stored in db

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password_confirmation
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self


class UserUpdateSchema(BaseModel):
    username: Optional[Annotated[str, Field(min_length=3, max_length=49)]] = None
    first_name: Optional[Annotated[str, Field(max_length=49)]] = None
    last_name: Optional[Annotated[str, Field(max_length=49)]] = None
    new_password: Optional[Annotated[str, Field(min_length=8, max_length=255)]] = None
    password: Optional[Annotated[str, Field(max_length=255)]] = None  # password needed to cofirm user intentions

    @model_validator(mode='after')
    def check_password_present_on_change(self) -> Self:
        if self.new_password and not self.password:
            raise ValueError('password is required to change password')
        return self


class UserDetail(UserSchema):
    first_name: Union[Annotated[str, Field(max_length=49)], None]
    last_name: Union[Annotated[str, Field(max_length=49)], None]


class UserList(BaseModel):
    users: list[UserSchema] = []
