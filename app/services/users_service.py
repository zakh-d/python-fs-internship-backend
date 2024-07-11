from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.schemas.user_shema import UserSchema, UserList, UserSignUpSchema


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

        user_repository.create_user_with_hashed_password(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password
        )

        await user_repository.commit_me()
