from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import CompanyAction, CompanyActionType
from app.repositories.repository_base import RepositoryBase


class CompanyActionRepository(RepositoryBase):
    async def get_all_invites_by_company(self, company_id: UUID) -> list[CompanyAction]:
        query = select(CompanyAction).where(
            CompanyAction.company_id == company_id and CompanyAction.type == CompanyActionType.INVITATION
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all_invites_by_user(self, user_id: UUID) -> list[CompanyAction]:
        query = select(CompanyAction).where(
            CompanyAction.user_id == user_id and CompanyAction.type == CompanyActionType.INVITATION
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, company_id: UUID, user_id: UUID, type: CompanyActionType) -> Union[CompanyAction, None]:
        action = CompanyAction(company_id=company_id, user_id=user_id, type=type)
        self.db.add(action)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            return None
        await self.db.refresh(action)
        return action

    async def create_invintation(self, company_id: UUID, user_id: UUID) -> Union[CompanyAction, None]:
        return await self.create(company_id, user_id, CompanyActionType.INVITATION)

    async def create_request(self, company_id: UUID, user_id: UUID) -> Union[CompanyAction, None]:
        return await self.create(company_id, user_id, CompanyActionType.REQUEST)
