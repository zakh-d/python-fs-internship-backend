from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends

from app.db.models import Company, CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import CompanyCreateSchema, CompanyListSchema, CompanySchema
from app.schemas.user_shema import UserDetail

from .exceptions import (
    ActionNotFound,
    CompanyNotFoundException,
    CompanyPermissionException,
    UserAlreadyInvitedException,
)


class CompanyService:
    def __init__(
        self,
        company_repository: Annotated[CompanyRepository, Depends(CompanyRepository)],
        company_action_repository: Annotated[CompanyActionRepository, Depends(CompanyActionRepository)],
    ):
        self._company_repository = company_repository
        self._company_action_repository = company_action_repository

    def _user_has_edit_permission(self, company: Company, current_user: UserDetail) -> bool:
        # possible place for future is_admin check
        return company.owner_id == current_user.id

    def _user_has_delete_permission(self, company: Company, current_user: UserDetail) -> bool:
        # only admin can delete their company
        return company.owner_id == current_user.id

    async def _company_exists_and_user_has_permission(
        self, company_id: UUID, current_user: UserDetail, permission_func: Callable[[UUID, UUID], bool]
    ) -> Company:
        company = await self.check_company_exists(company_id)
        if not permission_func(company, current_user):
            raise CompanyPermissionException()
        return company

    async def check_company_exists(self, company_id: UUID) -> Company:
        company = await self._company_repository.get_company_by_id(company_id)
        if company is None:
            raise CompanyNotFoundException(company_id)
        return company

    async def get_all_companies(self, page: int, limit: int) -> CompanyListSchema:
        offset = (page - 1) * limit
        companies = await self._company_repository.get_all_companies(offset, limit)
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies],
            total_count=await self._company_repository.get_companies_count(),
        )

    async def get_company_by_id(self, company_id: UUID) -> CompanySchema:
        company = await self._company_repository.get_company_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        company.owner = await company.awaitable_attrs.owner
        return CompanySchema.model_validate(company)

    async def create_company(self, company_data: CompanyCreateSchema, current_user: UserDetail) -> CompanySchema:
        company = await self._company_repository.create_company(company_data, current_user.id)
        return CompanySchema.model_validate(company)

    async def update_company(
        self, company_id: UUID, company_data: CompanyCreateSchema, current_user: UserDetail
    ) -> CompanySchema:
        company = await self._company_exists_and_user_has_permission(
            company_id, current_user, self._user_has_edit_permission
        )
        company = await self._company_repository.update_company(company, company_data)
        return CompanySchema.model_validate(company)

    async def delete_company(self, company_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_delete_permission)
        await self._company_repository.delete_company_by_id(company_id)

    async def invite_user(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> CompanyActionSchema:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        intivation = await self._company_action_repository.create_invintation(company_id, user_id)
        if intivation is None:
            raise UserAlreadyInvitedException(user_id, company_id)
        return CompanyActionSchema.model_validate(intivation)

    async def get_invites_for_company(
        self,
        company_id: UUID,
        current_user: UserDetail,
    ) -> list[CompanyActionSchema]:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        return await self._company_action_repository.get_company_action_for_company_by_type(
            company_id, CompanyActionType.INVITATION
        )

    async def get_requests_to_company(
        self,
        company_id: UUID,
        current_user: UserDetail,
    ) -> list[CompanyActionSchema]:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        return await self._company_action_repository.get_company_action_for_company_by_type(
            company_id, CompanyActionType.REQUEST
        )

    async def accept_request(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> CompanyActionSchema:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        request = await self._company_action_repository.get_company_action_by_company_and_user(
            company_id, user_id, CompanyActionType.REQUEST
        )
        if not request:
            raise ActionNotFound(CompanyActionType.REQUEST)
        return await self._company_action_repository.update(request, CompanyActionType.MEMBERSHIP)

    async def reject_request(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.REQUEST)

    async def cancel_invite(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.INVITATION)
