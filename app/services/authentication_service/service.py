from uuid import UUID
from fastapi import Depends
import jwt
from datetime import datetime, timedelta, timezone
from passlib.hash import argon2
from typing import Annotated, Union

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.user_shema import UserDetail, UserSchema, UserSignInSchema


class AuthenticationService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository

    async def authenticate(self, user_signin_request: UserSignInSchema) -> Union[UserSchema, None]:
        user = await self.user_repository.get_user_by_email(user_signin_request.email)

        if user is None:
            return None

        if not argon2.verify(user_signin_request.password, user.hashed_password):
            return None

        return UserSchema.model_validate(user)

    def generate_jwt_token(self, user: UserSchema) -> str:
        now_plus_expiration = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        token = jwt.encode(
            {
                'user_id': user.id.hex,
                'exp': now_plus_expiration,
            },
            settings.JWT_SECRET,
            algorithm='HS256',
        )
        return token

    def _get_user_id_from_token(self, token: str) -> Union[UUID, None]:
        try:
            token_payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
            return UUID(token_payload.get('user_id'))
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def _get_email_form_auth0_token(self, token: str) -> Union[str, None]:
        try:
            token_payload = jwt.decode(
                token, settings.AUTH0_SIGNING_SECRET, algorithms=['HS256'], audience=settings.AUTH0_AUDIENCE
            )
            return token_payload.get(settings.AUTH0_EMAIL_NAME_IN_TOKEN)
        except Exception:
            return None

    async def get_user_by_token(self, token: str) -> Union[UserDetail, None]:
        user_id = self._get_user_id_from_token(token)
        if user_id is not None:
            user = await self.user_repository.get_user_by_id(user_id)
            return user

        user_email = self._get_email_form_auth0_token(token)
        print('Extracting email from token')
        if user_email is not None:
            print('Email extracted')
            user = await self.user_repository.get_user_by_email_or_create(user_email)
            return user
        return None
