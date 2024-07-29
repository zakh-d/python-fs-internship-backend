from typing import Annotated, Union

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import Invitation, Request
from app.repositories.repository_base import RepositoryBase

T = Union[Invitation, Request]


class InvitationRequestRepository(RepositoryBase):
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        super().__init__(db)
        self.table = Invitation

    def change_table(self, table: T) -> None:
        if table in [Invitation, Request]:
            self.table = table

    async def get_all_by_user_id(self, user_id: str) -> T:
        results = await self.db.execute(self.table.select().where(self.table.user_id == user_id))
        return results.scalars().all()

    async def create(self, user_id: str, company_id: str) -> Union[T, None]:
        item = self.table(user_id=user_id, company_id=company_id)
        self.db.add(item)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            return None
        await self.db.refresh(item)
        return item
