from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user_shema import UserSignUpSchema


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def get_all_users(self):
        results = await self.db.execute(select(User))
        return results.scalars().all()

    def create_user(self, user_data: UserSignUpSchema):
        user = User(**user_data)
        self.db.add(user)

    async def commit_me(self):
        await self.db.commit()
        await self.db.refresh()
