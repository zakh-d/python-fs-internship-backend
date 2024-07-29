from typing import Annotated

from fastapi import Depends

from app.db.models import Company, Request
from app.repositories.company_repository import CompanyRepository
from app.repositories.invitation_request_repository import InvitationRequestRepository
from app.schemas.company_schema import CompanyCreateSchema, CompanyListSchema, CompanySchema
from app.schemas.invitation_request_schema import InvitationOrRequestCreateSchema, InvitationOrRequestSchema
from app.schemas.user_shema import UserDetail

from .exceptions import CompanyNotFoundException, CompanyPermissionException, UserAlreadyInvitedException


class CompanyService:
    def __init__(
        self,
        company_repository: Annotated[CompanyRepository, Depends(CompanyRepository)],
        intivation_repository: Annotated[InvitationRequestRepository, Depends(InvitationRequestRepository)],
        request_repository: Annotated[InvitationRequestRepository, Depends(InvitationRequestRepository)],
    ):
        self._company_repository = company_repository
        self._invitation_repository = intivation_repository
        self._request_repository = request_repository
        self._request_repository.change_table(Request)

    async def get_all_companies(self, page: int, limit: int) -> CompanyListSchema:
        offset = (page - 1) * limit
        companies = await self._company_repository.get_all_companies(offset, limit)
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies],
            total_count=await self._company_repository.get_companies_count(),
        )

    async def get_company_by_id(self, company_id: str) -> CompanySchema:
        company = await self._company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        company.owner = await company.awaitable_attrs.owner
        return CompanySchema.model_validate(company)

    async def create_company(self, company_data: CompanyCreateSchema, current_user: UserDetail) -> CompanySchema:
        company = await self._company_repository.create_company(company_data, current_user.id)
        return CompanySchema.model_validate(company)

    async def update_company(
        self, company_id: str, company_data: CompanyCreateSchema, current_user: UserDetail
    ) -> CompanySchema:
        company = await self._company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        if not self._user_has_edit_permission(company, current_user):
            raise CompanyPermissionException()
        company = await self._company_repository.update_company(company, company_data)
        return CompanySchema.model_validate(company)

    async def delete_company(self, company_id: str, current_user: UserDetail) -> None:
        company = await self._company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        if not self._user_has_delete_permission(company, current_user):
            raise CompanyPermissionException()
        await self._company_repository.delete_company_by_id(company_id)

    def _user_has_edit_permission(self, company: Company, current_user: UserDetail) -> bool:
        # possible place for future is_admin check
        return company.owner_id == current_user.id

    def _user_has_delete_permission(self, company: Company, current_user: UserDetail) -> bool:
        # only admin can delete their company
        return company.owner_id == current_user.id

    async def create_invitation_for_user(
        self, intivation: InvitationOrRequestCreateSchema, current_user: UserDetail
    ) -> InvitationOrRequestSchema:
        company = await self._company_repository.get_company_by_id(intivation.company_id)
        if company is None:
            raise CompanyNotFoundException(intivation.company_id)
        if not self._user_has_edit_permission(company, current_user):
            raise CompanyPermissionException()
        intivation = await self._invitation_repository.create(intivation.user_id, intivation.company_id)
        if intivation is None:
            raise UserAlreadyInvitedException(intivation.user_id, intivation.company_id)
        return InvitationOrRequestSchema.model_validate(intivation)
