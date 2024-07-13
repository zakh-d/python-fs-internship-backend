from typing import Annotated, Union
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import User


class UserRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db: AsyncSession = db

    async def get_all_users(self) -> list[User]:
        results = await self.db.execute(select(User))
        return results.scalars().all()

    async def get_user_by_id(self, user_id: UUID) -> User:
        results = await self.db.execute(select(User).where(User.id == user_id))
        return results.scalars().first()

    async def get_user_by_username(self, username: str) -> User:
        results = await self.db.execute(select(User).where(User.username == username))
        return results.scalars().first()

    def create_user_with_hashed_password(self,
                                         username: str,
                                         first_name: Union[str, None],
                                         last_name: Union[str, None],
                                         email: str,
                                         hashed_password: str) -> User:
        user = User()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.hashed_password = hashed_password
        self.db.add(user)

        return user

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)

    def update_user(self, user: User, user_data: dict) -> None:
        for field, value in user_data.items():
            setattr(user, field, value)

    async def commit_me(self, user: User, refresh: bool = True) -> None:
        await self.db.commit()
        if refresh:
            await self.db.refresh(user)
