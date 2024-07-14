from uuid import UUID
import jwt
from datetime import datetime, timedelta, timezone
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.user_shema import UserSchema, UserSignInSchema


class AuthenticationService:

    @staticmethod
    async def authenticate(db: AsyncSession, user_signin_request: UserSignInSchema) -> Union[UserSchema, None]:
        user_repository = UserRepository(db)

        user = await user_repository.get_user_by_username(user_signin_request.username)

        if user is None:
            return None

        if not argon2.verify(user_signin_request.password, user.hashed_password):
            return None

        return UserSchema.model_validate(user)

    @staticmethod
    def generate_jwt_token(user: UserSchema) -> str:
        now_plus_expiration = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        token = jwt.encode({
            "user_id": user.id.hex,
            "exp": now_plus_expiration,
        }, settings.JWT_SECRET, algorithm="HS256")
        return token

    @staticmethod
    def get_user_id_from_token(token: str) -> Union[UUID, None]:
        try:
            token_payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return UUID(token_payload.get("user_id"))
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
