from typing import Union
from uuid import UUID

from sqlalchemy import and_, delete, select

from app.db.models import Company, CompanyAction, CompanyActionType, User
from app.repositories.repository_base import RepositoryBase


class CompanyActionRepository(RepositoryBase):
    async def get_company_action_for_company_by_type(
        self, company_id: UUID, _type: CompanyActionType
    ) -> list[CompanyAction]:
        query = select(CompanyAction).where(and_(CompanyAction.company_id == company_id, CompanyAction.type == _type))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_users_related_to_company(self, company_id: UUID, relation: CompanyActionType) -> list[User]:
        query = (
            select(User)
            .join_from(CompanyAction, User)
            .where(and_(CompanyAction.company_id == company_id, CompanyAction.type == relation))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_companies_related_to_user(self, user_id: UUID, relation: CompanyActionType) -> list[Company]:
        query = (
            select(Company)
            .join_from(CompanyAction, Company)
            .where(and_(CompanyAction.user_id == user_id, CompanyAction.type == relation))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_action_for_user_by_type(self, user_id: UUID, _type: CompanyActionType) -> list[CompanyAction]:
        query = select(CompanyAction).where(and_(CompanyAction.user_id == user_id, CompanyAction.type == _type))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_action_by_company_and_user(
        self, company_id: UUID, user_id: UUID, _type: CompanyActionType
    ) -> Union[CompanyAction, None]:
        query = select(CompanyAction).where(
            and_(CompanyAction.company_id == company_id, CompanyAction.user_id == user_id, CompanyAction.type == _type)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    def create(self, company_id: UUID, user_id: UUID, type: CompanyActionType) -> Union[CompanyAction, None]:
        action = CompanyAction(company_id=company_id, user_id=user_id, type=type)
        self.db.add(action)
        return action

    async def create_invintation(self, company_id: UUID, user_id: UUID) -> Union[CompanyAction, None]:
        invite = self.create(company_id, user_id, CompanyActionType.INVITATION)
        try:
            await self.commit()
            return invite
        except Exception:
            return None

    async def create_request(self, company_id: UUID, user_id: UUID) -> Union[CompanyAction, None]:
        request = self.create(company_id, user_id, CompanyActionType.REQUEST)
        try:
            await self.commit()
            return request
        except Exception:
            return None

    async def update(self, company_action: CompanyAction, new_type: CompanyActionType) -> CompanyAction:
        company_action.type = new_type
        self.db.add(company_action)
        await self.db.commit()
        await self.db.refresh(company_action)
        return company_action

    async def delete(self, company_id: UUID, user_id: UUID, _type: CompanyActionType) -> None:
        await self.db.execute(
            delete(CompanyAction).where(
                and_(
                    CompanyAction.company_id == company_id,
                    CompanyAction.user_id == user_id,
                    CompanyAction.type == _type,
                )
            )
        )
        await self.db.commit()
