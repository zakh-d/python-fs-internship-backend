from typing import Annotated, TypeVar
from uuid import UUID
from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db

T = TypeVar('T')


class RepositoryBase:

    def __init__(self, table: T, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db
        self.table = table

    async def _get_all_items(self) -> list[T]:
        results = await self.db.execute(select(self.table))
        return results.scalars().all()

    async def _get_item_by_id(self, item_id: UUID) -> T:
        results = await self.db.execute(select(self.table).where(self.table.id == item_id))
        return results.scalars().first()

    async def _delete_item_by_id(self, item_id: UUID) -> None:
        await self.db.execute(delete(self.table).where(self.table.id == item_id))
