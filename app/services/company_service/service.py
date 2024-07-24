from typing import Annotated

from app.repositories.company_repository import CompanyRepository
from app.schemas.company_schema import CompanySchema, CompanyListSchema, CompanyCreateSchema
from app.schemas.user_shema import UserDetail


class CompanyService:

    def __init__(self, company_repository: Annotated[CompanyRepository, CompanyRepository]):
        self.company_repository = company_repository

    async def get_all_companies(self) -> CompanyListSchema:
        companies = await self.company_repository.get_all_companies()
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies]
        )

    async def get_company_by_id(self, company_id: str) -> CompanySchema:
        company = await self.company_repository.get_company_by_id(company_id)
        return CompanySchema.model_validate(company)

    async def create_company(self, company_data: CompanyCreateSchema, current_user: UserDetail) -> CompanySchema:
        company = await self.company_repository.create_company(company_data, current_user.id)
        return CompanySchema.model_validate(company)
