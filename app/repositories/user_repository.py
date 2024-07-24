from typing import Union
from uuid import UUID

from sqlalchemy import select

from app.db.models import User
from app.repositories.repository_base import RepositoryBase


class UserRepository(RepositoryBase):

    async def get_all_users(self) -> list[User]:
        return await self._get_all_items(User)

    async def get_user_by_id(self, user_id: UUID) -> User:
        return await self._get_item_by_id(user_id, User)

    async def get_user_by_email(self, email: str) -> User:
        results = await self.db.execute(select(User).where(User.email == email))
        return results.scalars().first()

    def create_user_with_hashed_password(
        self, username: str, first_name: Union[str, None], last_name: Union[str, None], email: str, hashed_password: str
    ) -> User:
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
