import contextlib
from typing import Annotated, TypeVar
from uuid import UUID

from fastapi import Depends
from sqlalchemy import ColumnElement, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

T = TypeVar('T')


class RepositoryBase:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def _get_all_items(self, offset: int, limit: int, table: T) -> list[T]:
        results = await self.db.execute(select(table).offset(offset).limit(limit))
        return results.scalars().all()

    async def _get_all_meeting_condition(
        self, offset: int, limit: int, condition: ColumnElement[bool], table: T
    ) -> list[T]:
        results = await self.db.execute(select(table).where(condition).offset(offset).limit(limit))
        return results.scalars().all()

    async def _get_items_count(self, table: T) -> int:
        results = await self.db.execute(select(func.count(table.id)))
        return results.scalar_one()

    async def _get_items_count_by_condition(self, condition: ColumnElement[bool], table: T) -> int:
        results = await self.db.execute(select(func.count(table.id)).where(condition))
        return results.scalar_one()

    async def _get_item_by_id(self, item_id: UUID, table: T) -> T:
        results = await self.db.execute(select(table).where(table.id == item_id))
        return results.scalars().first()

    async def _delete_item_by_id(self, item_id: UUID, table: T) -> None:
        await self.db.execute(delete(table).where(table.id == item_id))

    async def commit(self):
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

    @contextlib.asynccontextmanager
    async def unit(self):
        yield
        await self.commit()
