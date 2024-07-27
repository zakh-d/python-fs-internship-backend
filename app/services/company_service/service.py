from typing import Annotated

from fastapi import Depends

from app.db.models import Company
from app.repositories.company_repository import CompanyRepository
from app.schemas.company_schema import CompanyCreateSchema, CompanyListSchema, CompanySchema
from app.schemas.user_shema import UserDetail

from .exceptions import CompanyNotFoundException, CompanyPermissionException


class CompanyService:
    def __init__(self, company_repository: Annotated[CompanyRepository, Depends(CompanyRepository)]):
        self.company_repository = company_repository

    async def get_all_companies(self, page: int, limit: int) -> CompanyListSchema:
        offset = (page - 1) * limit
        companies = await self.company_repository.get_all_companies(offset, limit)
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies],
            total_count=await self.company_repository.get_companies_count(),
        )

    async def get_company_by_id(self, company_id: str) -> CompanySchema:
        company = await self.company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        company.owner = await company.awaitable_attrs.owner
        return CompanySchema.model_validate(company)

    async def create_company(self, company_data: CompanyCreateSchema, current_user: UserDetail) -> CompanySchema:
        company = await self.company_repository.create_company(company_data, current_user.id)
        return CompanySchema.model_validate(company)

    async def update_company(
        self, company_id: str, company_data: CompanyCreateSchema, current_user: UserDetail
    ) -> CompanySchema:
        company = await self.company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        if not self._user_has_edit_permission(company, current_user):
            raise CompanyPermissionException()
        company = await self.company_repository.update_company(company, company_data)
        return CompanySchema.model_validate(company)

    async def delete_company(self, company_id: str, current_user: UserDetail) -> None:
        company = await self.company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        if not self._user_has_delete_permission(company, current_user):
            raise CompanyPermissionException()
        await self.company_repository.delete_company_by_id(company_id)

    def _user_has_edit_permission(self, company: Company, current_user: UserDetail) -> bool:
        # possible place for future is_admin check
        return company.owner_id == current_user.id

    def _user_has_delete_permission(self, company: Company, current_user: UserDetail) -> bool:
        # only admin can delete their company
        return company.owner_id == current_user.id
