from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.schemas.user_shema import UserSchema


class UserService:

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[UserSchema]:
        user_repository = UserRepository(db)
        users = await user_repository.get_all_users()
        return [UserSchema.model_validate(user) for user in users]

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserSchema):
        user_repository = UserRepository(db)
        user_repository.create_user(user_data)
        await user_repository.commit_me()
