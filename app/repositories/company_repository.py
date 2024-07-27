from typing import Union
from uuid import UUID

from app.db.models import Company
from app.repositories.repository_base import RepositoryBase
from app.schemas.company_schema import CompanyCreateSchema, CompanyUpdateSchema


class CompanyRepository(RepositoryBase):
    async def get_all_companies(self, offset: int, limit: int) -> list[Company]:
        return await self._get_all_items(offset, limit, Company)

    async def get_companies_count(self) -> int:
        return await self._get_items_count(Company)

    async def get_company_by_id(self, company_id: UUID) -> Union[Company, None]:
        return await self._get_item_by_id(company_id, Company)

    async def delete_company_by_id(self, company_id: UUID) -> None:
        await self._delete_item_by_id(company_id, Company)
        await self.db.commit()

    async def create_company(self, company_data: CompanyCreateSchema, owner_id: UUID) -> Company:
        company = Company(
            name=company_data.name, description=company_data.description, owner_id=owner_id, hidden=company_data.hidden
        )
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def update_company(self, company: Company, company_data: CompanyUpdateSchema) -> Company:
        new_data = company_data.model_dump(exclude_none=True)
        for field, value in new_data.items():
            setattr(company, field, value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
