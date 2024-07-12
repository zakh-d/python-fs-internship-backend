from passlib.hash import argon2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.schemas.user_shema import UserDetail, UserSchema, UserList, UserSignUpSchema, UserUpdateSchema
from app.services.users_service.exceptions import (
    UserAlreadyExistsException, UserNotFoundException, InvalidPasswordException
)
from app.utils.error_parser import get_conflicting_field
from app.utils.logging import logger


class UserService:

    @staticmethod
    async def get_all_users(db: AsyncSession) -> UserList:
        user_repository = UserRepository(db)
        users = await user_repository.get_all_users()
        return UserList(users=[UserSchema.model_validate(user) for user in users])

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserSignUpSchema):
        user_repository = UserRepository(db)

        hashed_password = argon2.hash(user_data.password)

        created_user = user_repository.create_user_with_hashed_password(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        try:
            await user_repository.commit_me(created_user)
            logger.info(f"User with id: {created_user.id} created successfully!")
        except IntegrityError as e:
            conflicting_field, value = get_conflicting_field(e)
            logger.error(f"User with {conflicting_field}: '{value}' already exists!")
            raise UserAlreadyExistsException(f"User with {conflicting_field}: '{value}' already exists!")
        return UserSchema.model_validate(created_user)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        user_repository = UserRepository(db)
        user = await user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)
        return UserDetail.model_validate(user)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdateSchema) -> UserDetail:
        user_repository = UserRepository(db)
        user = await user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)

        if not argon2.verify(user_data.password, user.hashed_password):
            raise InvalidPasswordException()

        user_repository.update_user(user, user_data.model_dump(exclude_unset=True, exclude={'password'}))
        try:
            await user_repository.commit_me(user)
            logger.info(f"User with id: {user.id} updated successfully!")
        except IntegrityError as e:
            conflicting_field, value = get_conflicting_field(e)
            logger.error(f"Cannot update user to {conflicting_field}: '{value}'!")
            raise UserAlreadyExistsException(f"User with {conflicting_field}: '{value}' already exists!")

        return UserDetail.model_validate(user)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):
        user_repository = UserRepository(db)
        user = await user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)

        await user_repository.delete_user(user)
        await user_repository.commit_me(user, refresh=False)
        logger.info(f"User with id: {user.id} deleted successfully!")
