from typing import Callable, Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Company, CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizz_repository import QuizzRepository
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    CompanyDetailWithIsMemberSchema,
    CompanyListSchema,
    CompanySchema,
)
from app.schemas.user_shema import UserDetail, UserInCompanyList, UserInCompanySchema, UserList, UserSchema
from app.services.notification_service import NotificationService

from .exceptions import (
    ActionNotFound,
    CompanyActionException,
    CompanyNotFoundException,
    CompanyPermissionException,
    UserAlreadyInvitedException,
)


class CompanyService:
    def __init__(self, session: AsyncSession):
        self._company_repository = CompanyRepository(session)
        self._company_action_repository = CompanyActionRepository(session)
        self._quizz_repository = QuizzRepository(session)
        self._notification_service = NotificationService(session)

    def _user_has_edit_permission(self, company: Company, current_user: UserDetail) -> bool:
        # possible place for future is_admin check
        return company.owner_id == current_user.id

    def _user_has_delete_permission(self, company: Company, current_user: UserDetail) -> bool:
        # only owner can delete their company
        return company.owner_id == current_user.id

    def _user_is_company_owner(self, company: Company, current_user: UserDetail) -> bool:
        return company.owner_id == current_user.id

    async def _company_exists_and_user_has_permission(
        self, company_id: UUID, current_user: UserDetail, permission_func: Callable[[Company, UserDetail], bool]
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

    async def check_company_exists_and_is_public(self, company_id: UUID) -> Company:
        company = await self.check_company_exists(company_id)
        if company.hidden:
            raise CompanyNotFoundException(company_id)
        return company

    async def check_owner_or_admin(self, company_id: UUID, user_id: UUID) -> Company:
        company = await self.check_company_exists(company_id)
        is_admin = await self._company_action_repository.get_by_company_user_and_type(
            company_id=company_id, user_id=user_id, _type=CompanyActionType.ADMIN
        )
        if company.owner_id != user_id and is_admin is None:
            raise CompanyNotFoundException(company_id)
        return company

    async def check_is_member(self, company_id: UUID, user_id: UUID) -> Company:
        company = await self.check_company_exists(company_id)
        is_member = await self._company_action_repository.get_by_company_user_and_type(
            company_id=company_id, user_id=user_id, _type=CompanyActionType.MEMBERSHIP
        )
        is_admin = await self._company_action_repository.get_by_company_user_and_type(
            company_id=company_id, user_id=user_id, _type=CompanyActionType.ADMIN
        )
        if is_member is None and is_admin is None:
            raise CompanyNotFoundException(company_id)
        return company

    async def get_all_companies(self, page: int, limit: int) -> CompanyListSchema:
        offset = (page - 1) * limit
        companies, count = await self._company_repository.get_all_companies(offset, limit)
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=count
        )

    async def get_companies_by_owner_id(
        self, owner_id: UUID, including_hidden: bool, page: int, limit: int
    ) -> CompanyListSchema:
        offset = (page - 1) * limit
        companies, count = await self._company_repository.get_companies_by_owner_id(
            owner_id, including_hidden, offset, limit
        )
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=count
        )

    async def get_company_by_id(self, company_id: UUID, current_user: UserDetail) -> CompanyDetailWithIsMemberSchema:
        company = await self._company_repository.get_company_by_id(company_id)
        membership = await self._company_action_repository.get_by_company_and_user(
            company_id=company_id, user_id=current_user.id
        )
        if not company:
            raise CompanyNotFoundException(company_id)
        if company.hidden and company.owner_id != current_user.id and membership is None:
            raise CompanyNotFoundException(company_id)
        if company.hidden and membership.type not in [CompanyActionType.MEMBERSHIP, CompanyActionType.ADMIN]:
            raise CompanyNotFoundException(company_id)
        company.owner = await company.awaitable_attrs.owner
        status = 'yes'
        if membership is None:
            status = 'no'
        elif membership.type == CompanyActionType.REQUEST:
            status = 'pending_request'
        elif membership.type == CompanyActionType.INVITATION:
            status = 'pending_invite'
        company_detail_with_is_member = CompanyDetailWithIsMemberSchema(
            **CompanyDetailSchema.model_validate(company).dict(), is_member=status
        )
        return company_detail_with_is_member

    async def create_company(self, company_data: CompanyCreateSchema, current_user: UserDetail) -> CompanySchema:
        async with self._company_repository.unit():
            company = self._company_repository.create_company(company_data, current_user.id)
            await self._company_repository.db.flush()
            await self._company_repository.db.refresh(company)
            self._company_action_repository.create(company.id, current_user.id, CompanyActionType.MEMBERSHIP)
            company.owner = await company.awaitable_attrs.owner
            return CompanySchema.model_validate(company)

    async def update_company(
        self, company_id: UUID, company_data: CompanyCreateSchema, current_user: UserDetail
    ) -> CompanyDetailSchema:
        company = await self._company_exists_and_user_has_permission(
            company_id, current_user, self._user_has_edit_permission
        )
        company = self._company_repository.update_company(company, company_data)
        await self._company_repository.commit()
        company.owner = await company.awaitable_attrs.owner
        return CompanyDetailSchema.model_validate(company)

    async def delete_company(self, company_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_delete_permission)
        await self._company_repository.delete_company_by_id_and_commit(company_id)

    async def get_user_role_in_company(
        self, company_id: UUID, user_id: UUID
    ) -> Literal['none', 'member', 'admin', 'owner']:
        company = await self.check_company_exists(company_id)
        if company.owner_id == user_id:
            return 'owner'
        action = await self._company_action_repository.get_by_company_and_user(company_id, user_id)
        if action is None:
            if company.hidden:
                raise CompanyNotFoundException(company_id)
            return 'none'
        if action.type == CompanyActionType.MEMBERSHIP:
            return 'member'
        if action.type == CompanyActionType.ADMIN:
            return 'admin'
        return 'none'

    async def invite_user(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> CompanyActionSchema:
        company = await self._company_exists_and_user_has_permission(
            company_id, current_user, self._user_has_edit_permission
        )
        intivation = await self._company_action_repository.create_invintation(company_id, user_id)
        if intivation is None:
            raise UserAlreadyInvitedException(user_id, company_id)
        await self._notification_service.send_notification_to_user(
            to_user_id=user_id,
            title='Company invitation',
            body=f'You have been invited to join company {company.name}',
        )
        return CompanyActionSchema.model_validate(intivation)

    async def _get_related_users_list(self, company_id: UUID, relation: CompanyActionType) -> UserList:
        related_users = await self._company_action_repository.get_users_related_to_company(company_id, relation)
        return UserList(
            users=[UserSchema.model_validate(user) for user in related_users], total_count=len(related_users)
        )

    async def get_invites_for_company(
        self,
        company_id: UUID,
        current_user: UserDetail,
    ) -> UserList:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        return await self._get_related_users_list(company_id, CompanyActionType.INVITATION)

    async def get_requests_to_company(
        self,
        company_id: UUID,
        current_user: UserDetail,
    ) -> UserList:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        return await self._get_related_users_list(company_id, CompanyActionType.REQUEST)

    async def get_company_members(
        self,
        company_id: UUID,
    ) -> UserInCompanyList:
        company = await self.check_company_exists(company_id)

        members = await self._quizz_repository.get_company_members_with_lastest_complition_date(company.id)

        schema_list_of_users = []

        for user in members:
            user_role = 'member'
            if user.id == company.owner_id:
                user_role = 'owner'
            if user.role == CompanyActionType.ADMIN:
                user_role = 'admin'
            user_in_company = UserInCompanySchema(
                id=user.id,
                email=user.email,
                username=user.username,
                created_at=user.created_at,
                updated_at=user.updated_at,
                role=user_role,
                lastest_quizz_comleted_at=user.lastest_completion,
            )
            schema_list_of_users.append(user_in_company)

        return UserInCompanyList(users=schema_list_of_users, total_count=len(schema_list_of_users))

    async def accept_request(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> CompanyActionSchema:
        company = await self._company_exists_and_user_has_permission(
            company_id, current_user, self._user_has_edit_permission
        )
        request = await self._company_action_repository.get_by_company_user_and_type(
            company_id, user_id, CompanyActionType.REQUEST
        )
        if not request:
            raise ActionNotFound(CompanyActionType.REQUEST)
        await self._notification_service.send_notification_to_user(
            to_user_id=user_id,
            title='Company request accepted',
            body=f'Your request to join {company.name} has been accepted',
        )
        return await self._company_action_repository.update(request, CompanyActionType.MEMBERSHIP)

    async def reject_request(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.REQUEST)

    async def cancel_invite(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_has_edit_permission)
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.INVITATION)

    async def remove_member(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        company = await self.check_company_exists(company_id)
        if current_user.id != user_id and not self._user_has_edit_permission(company, current_user):
            raise CompanyPermissionException()

        if company.owner_id == user_id:
            raise CompanyActionException('Owner cannot be removed from company')
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.MEMBERSHIP)
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.ADMIN)

    async def get_admin_list(
        self,
        company_id: UUID,
        current_user: UserDetail,
    ) -> UserList:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_is_company_owner)
        admins = await self._company_action_repository.get_users_related_to_company(company_id, CompanyActionType.ADMIN)
        return UserList(users=[UserSchema.model_validate(user) for user in admins], total_count=len(admins))

    async def add_admin(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> CompanyActionSchema:
        company = await self._company_exists_and_user_has_permission(
            company_id, current_user, self._user_is_company_owner
        )
        if company.owner_id == user_id:
            raise CompanyActionException('Cannot assign owner as an admin')
        membership = await self._company_action_repository.get_by_company_user_and_type(
            company_id, user_id, CompanyActionType.MEMBERSHIP
        )
        if not membership:
            raise ActionNotFound(CompanyActionType.MEMBERSHIP)
        admin_role = await self._company_action_repository.update(membership, CompanyActionType.ADMIN)
        await self._notification_service.send_notification_to_user(
            to_user_id=user_id,
            title='Company admin role',
            body=f'You have been assigned as an admin in company {company.name}',
        )
        return CompanyActionSchema.model_validate(admin_role)

    async def remove_admin(self, company_id: UUID, user_id: UUID, current_user: UserDetail) -> None:
        await self._company_exists_and_user_has_permission(company_id, current_user, self._user_is_company_owner)
        admin_role = await self._company_action_repository.get_by_company_user_and_type(
            company_id, user_id, CompanyActionType.ADMIN
        )
        if not admin_role:
            raise ActionNotFound(CompanyActionType.ADMIN)
        membership = await self._company_action_repository.update(admin_role, CompanyActionType.MEMBERSHIP)
        return membership

    async def get_companies_user_is_part_of(self, user_id: UUID) -> CompanyListSchema:
        companies = await self._company_action_repository.get_companies_user_is_part_of(user_id)
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=len(companies)
        )
