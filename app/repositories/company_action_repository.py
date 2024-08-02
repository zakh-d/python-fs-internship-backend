from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import CompanyAction, CompanyActionType
from app.repositories.repository_base import RepositoryBase


class CompanyActionRepository(RepositoryBase):
    async def get_company_action_for_company_by_type(
        self, company_id: UUID, _type: CompanyActionType
    ) -> list[CompanyAction]:
        query = select(CompanyAction).where(CompanyAction.company_id == company_id and CompanyAction.type == _type)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_action_for_user_by_type(self, user_id: UUID, _type: CompanyActionType) -> list[CompanyAction]:
        query = select(CompanyAction).where(CompanyAction.user_id == user_id and CompanyAction.type == _type)
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

    async def update(self, company_action: CompanyAction, new_type: CompanyActionType) -> CompanyAction:
        company_action.type = new_type
        self.db.add(company_action)
        await self.db.commit()
        await self.db.refresh(company_action)
        return company_action
