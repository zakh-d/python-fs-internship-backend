from typing import Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def get_all_users(self):
        results = await self.db.execute(select(User))
        return results.scalars().all()

    def create_user_with_hashed_password(self,
                                         username: str,
                                         first_name: Union[str, None],
                                         last_name: Union[str, None],
                                         email: str,
                                         hashed_password: str):
        user = User()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.hashed_password = hashed_password
        self.db.add(user)

    async def commit_me(self):
        await self.db.commit()
        await self.db.refresh()
