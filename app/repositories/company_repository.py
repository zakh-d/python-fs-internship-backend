from app.db.models import Company
from app.repositories.repository_base import RepositoryBase


class CompanyRepository(RepositoryBase):

    def __init__(self):
        super().__init__(Company)

    async def get_all_companies(self):
        return await super()._get_all_items()

    async def get_company_by_id(self, company_id):
        return await super()._get_item_by_id(company_id)

    async def delete_company_by_id(self, company_id):
        await super()._delete_item(company_id)
