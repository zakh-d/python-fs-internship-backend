from app.db.models import Company
from app.repositories.repository_base import RepositoryBase


class CompanyRepository(RepositoryBase):

    async def get_all_companies(self):
        return await self._get_all_items(Company)

    async def get_company_by_id(self, company_id):
        return await self._get_item_by_id(company_id, Company)

    async def delete_company_by_id(self, company_id):
        await self._delete_item(company_id, Company)
