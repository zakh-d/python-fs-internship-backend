from uuid import UUID
from app.db.models import Company
from app.repositories.repository_base import RepositoryBase
from app.schemas.company_schema import CompanyCreateSchema


class CompanyRepository(RepositoryBase):

    async def get_all_companies(self):
        return await self._get_all_items(Company)

    async def get_company_by_id(self, company_id):
        return await self._get_item_by_id(company_id, Company)

    async def delete_company_by_id(self, company_id):
        await self._delete_item(company_id, Company)

    async def create_company(self, company_data: CompanyCreateSchema, owner_id: UUID):
        company = Company(
            name=company_data.name,
            description=company_data.description,
            owner_id=owner_id
        )
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
