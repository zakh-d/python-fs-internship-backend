from typing import Annotated
from uuid import UUID

from fastapi import Depends
from passlib.hash import argon2
from sqlalchemy.exc import IntegrityError

from app.db.models import CompanyActionType
from app.repositories import CompanyActionRepository, UserRepository
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import CompanyListSchema, CompanySchema
from app.schemas.user_shema import UserDetail, UserList, UserSchema, UserSignUpSchema, UserUpdateSchema
from app.services.company_service.exceptions import ActionNotFound, UserAlreadyInvitedException
from app.services.notification_service.service import NotificationService
from app.services.users_service.exceptions import (
    InvalidPasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.utils.error_parser import get_conflicting_field
from app.utils.logging import logger


class UserService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        company_action_repository: Annotated[CompanyActionRepository, Depends(CompanyActionRepository)],
        notification_service: Annotated[NotificationService, Depends()],
    ):
        self._user_repository = user_repository
        self._company_action_repository = company_action_repository
        self._notification_service = notification_service
    async def get_all_users(self, page: int, limit: int) -> UserList:
        offset = (page - 1) * limit
        users = await self._user_repository.get_all_users(offset, limit)
        return UserList(
            users=[UserSchema.model_validate(user) for user in users],
            total_count=await self._user_repository.get_users_count(),
        )

    async def create_user(self, user_data: UserSignUpSchema) -> UserSchema:
        hashed_password = argon2.hash(user_data.password)

        created_user = self._user_repository.create_user_with_hashed_password(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        try:
            await self._user_repository.commit_me(created_user)
            logger.info(f'User with id: {created_user.id} created successfully!')
        except IntegrityError as e:
            conflicting_field, value = get_conflicting_field(e)
            logger.error(f"User with {conflicting_field}: '{value}' already exists!")
            raise UserAlreadyExistsException(conflicting_field, value)
        return UserSchema.model_validate(created_user)

    async def get_user_by_id(self, user_id: UUID) -> UserDetail:
        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)
        return UserDetail.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserDetail:
        user = await self._user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundException('email', email)
        return UserDetail.model_validate(user)

    async def update_user(self, user_id: UUID, user_data: UserUpdateSchema) -> UserDetail:
        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)

        if user_data.new_password and not argon2.verify(user_data.password, user.hashed_password):
            raise InvalidPasswordException()

        new_user_data = user_data.model_dump(exclude_unset=True, exclude={'password'})
        if user_data.new_password:
            logger.info(f'Updated password for user with id: {user.id}')
            new_user_data['hashed_password'] = argon2.hash(user_data.new_password)

        self._user_repository.update_user(user, new_user_data)
        try:
            await self._user_repository.commit_me(user)
            logger.info(f'User with id: {user.id} updated successfully!')
        except IntegrityError as e:
            conflicting_field, value = get_conflicting_field(e)
            logger.error(f"Cannot update user to {conflicting_field}: '{value}'!")
            raise UserAlreadyExistsException(conflicting_field, value)

        return UserDetail.model_validate(user)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException('id', user_id)

        await self._user_repository.delete_user(user)
        await self._user_repository.commit_me(user, refresh=False)
        logger.info(f'User with id: {user.id} deleted successfully!')

    async def get_user_invites(self, user_id: UUID) -> CompanyListSchema:
        companies = await self._company_action_repository.get_companies_related_to_user(
            user_id, CompanyActionType.INVITATION
        )
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=len(companies)
        )

    async def accept_invitation(self, user_id: UUID, company_id: UUID) -> None:
        invitation = await self._company_action_repository.get_by_company_user_and_type(
            company_id, user_id, CompanyActionType.INVITATION
        )
        if invitation is None:
            raise ActionNotFound(CompanyActionType.INVITATION)
        
        await self._notification_service.send_notification_to_user(
            to_user_id=(await invitation.awaitable_attrs.company).owner_id,
            title='New member',
            body=f'User: {(await invitation.awaitable_attrs.user).email} has accepted your invitation!'
        )
        await self._company_action_repository.update(invitation, CompanyActionType.MEMBERSHIP)

    async def reject_invitation(self, user_id: UUID, company_id: UUID) -> None:
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.INVITATION)

    async def get_user_requests(self, user_id: UUID) -> CompanyListSchema:
        companies = await self._company_action_repository.get_companies_related_to_user(
            user_id, CompanyActionType.REQUEST
        )
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=len(companies)
        )

    async def send_request(self, user_id: UUID, company_id: UUID) -> CompanyActionSchema:
        request = await self._company_action_repository.create_request(company_id, user_id)

        if request is None:
            raise UserAlreadyInvitedException(user_id=user_id, company_id=company_id)
        
        user = await self.get_user_by_id(user_id)
        await self._notification_service.send_notification_to_user(
            to_user_id=(await request.awaitable_attrs.company).owner_id,
            title='New request',
            body=f'User: {user.email} has requested to join your company!'
        )
        return CompanyActionSchema.model_validate(request)

    async def cancel_request(self, user_id: UUID, company_id: UUID) -> None:
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.REQUEST)

    async def get_user_companies(self, user_id: UUID) -> CompanyListSchema:
        companies = await self._company_action_repository.get_companies_related_to_user(
            user_id, CompanyActionType.MEMBERSHIP
        )
        for company in companies:
            company.owner = await company.awaitable_attrs.owner
        return CompanyListSchema(
            companies=[CompanySchema.model_validate(company) for company in companies], total_count=len(companies)
        )

    async def leave_company(self, user_id: UUID, company_id: UUID) -> None:
        await self._company_action_repository.delete(company_id, user_id, CompanyActionType.INVITATION)
