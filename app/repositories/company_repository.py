from typing import Union
from uuid import UUID

from sqlalchemy import and_

from app.db.models import Company
from app.repositories.repository_base import RepositoryBase
from app.schemas.company_schema import CompanyCreateSchema, CompanyUpdateSchema


class CompanyRepository(RepositoryBase):
    async def get_all_companies(self, offset: int, limit: int) -> tuple[list[Company], int]:
        condition = Company.hidden == False  # noqa
        companies = await self._get_all_meeting_condition(offset, limit, condition, Company)
        count = await self._get_items_count_by_condition(condition, Company)
        return companies, count

    async def get_companies_count(self) -> int:
        return await self._get_items_count(Company)

    async def get_companies_by_owner_id(
        self, owner_id: UUID, including_hidden: bool, offset: int, limit: int
    ) -> tuple[list[Company], int]:
        condition = and_(Company.owner_id == owner_id, Company.hidden == False)  # noqa
        if including_hidden:
            condition = Company.owner_id == owner_id
        companies = await self._get_all_meeting_condition(offset, limit, condition, Company)
        count = await self._get_items_count_by_condition(condition, Company)
        return companies, count

    async def get_company_by_id(self, company_id: UUID) -> Union[Company, None]:
        return await self._get_item_by_id(company_id, Company)

    async def delete_company_by_id_and_commit(self, company_id: UUID) -> None:
        await self._delete_item_by_id(company_id, Company)
        await self.db.commit()

    def create_company(self, company_data: CompanyCreateSchema, owner_id: UUID) -> Company:
        company = Company(
            name=company_data.name, description=company_data.description, owner_id=owner_id, hidden=company_data.hidden
        )
        self.db.add(company)
        return company

    def update_company(self, company: Company, company_data: CompanyUpdateSchema) -> Company:
        new_data = company_data.model_dump(exclude_none=True)
        for field, value in new_data.items():
            setattr(company, field, value)
        return company
