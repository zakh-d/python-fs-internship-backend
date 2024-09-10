import contextlib
from collections.abc import AsyncGenerator
from typing import TypeVar, Union
from uuid import UUID

from sqlalchemy import ColumnElement, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class RepositoryBase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_all_items(self, offset: int, limit: int, table: T) -> list[T]:
        query = select(table).offset(offset).limit(limit).order_by(table.created_at)
        results = await self.db.execute(query)
        return results.scalars().all()

    async def _get_all_meeting_condition(
        self, offset: int, limit: int, condition: ColumnElement[bool], table: T
    ) -> list[T]:
        query = select(table).where(condition).offset(offset).limit(limit).order_by(table.created_at)
        results = await self.db.execute(query)
        return results.scalars().all()

    async def _get_items_count(self, table: T) -> int:
        results = await self.db.execute(select(func.count(table.id)))
        return results.scalar_one()

    async def _get_items_count_by_condition(self, condition: ColumnElement[bool], table: T) -> int:
        results = await self.db.execute(select(func.count(table.id)).where(condition))
        return results.scalar_one()

    async def _get_item_by_id(self, item_id: UUID, table: T) -> Union[T, None]:
        results = await self.db.execute(select(table).where(table.id == item_id))
        return results.scalars().first()

    async def _delete_item_by_id(self, item_id: UUID, table: T) -> None:
        await self.db.execute(delete(table).where(table.id == item_id))

    async def commit(self) -> None:
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

    @contextlib.asynccontextmanager
    async def unit(self) -> AsyncGenerator[None, None]:
        yield
        await self.commit()
