from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    CompanyListSchema,
    CompanySchema,
    CompanyUpdateSchema,
)
from app.schemas.user_shema import UserDetail, UserList
from app.services.company_service.service import CompanyService

router = APIRouter()


@router.get('/')
async def get_companies(
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    _: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
    page: int = 1,
    limit: int = 10,
) -> CompanyListSchema:
    return await company_service.get_all_companies(page, limit)


@router.get('/my/')
async def get_my_companies(
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
    page: int = 1,
    limit: int = 10,
) -> CompanyListSchema:
    return await company_service.get_companies_by_owner_id(current_user.id, True, page, limit)


@router.get('/{company_id}')
async def get_company_by_id(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> CompanyDetailSchema:
    return await company_service.get_company_by_id(company_id, current_user)


@router.post('/')
async def create_company(
    company_data: CompanyCreateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanySchema:
    return await company_service.create_company(company_data, current_user)


@router.put('/{company_id}')
async def update_company(
    company_id: UUID,
    company_data: CompanyUpdateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanyDetailSchema:
    return await company_service.update_company(company_id, company_data, current_user)


@router.delete('/{company_id}')
async def delete_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> None:
    return await company_service.delete_company(company_id, current_user)


@router.get('/{company_id}/invites/')
async def get_invites_for_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> UserList:
    return await company_service.get_invites_for_company(company_id, current_user)


@router.post('/{company_id}/invites/{user_id}')
async def intive_user_to_company(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanyActionSchema:
    return await company_service.invite_user(company_id, user_id, current_user)


@router.delete('/{company_id}/invites/{user_id}')
async def cancel_invite(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    return await company_service.cancel_invite(company_id, user_id, current_user)


@router.get('/{company_id}/requests/')
async def get_requests_to_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> UserList:
    return await company_service.get_requests_to_company(company_id, current_user)


@router.post('/{company_id}/requests/{user_id}')
async def accept_request(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanyActionSchema:
    return await company_service.accept_request(company_id, user_id, current_user)


@router.delete('/{company_id}/requests/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def reject_request(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    return await company_service.reject_request(company_id, user_id, current_user)


@router.get('/{company_id}/members/', dependencies=[Depends(get_current_user)])
async def get_company_members(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> UserList:
    return await company_service.get_company_members(company_id)


@router.delete('/{company_id}/members/{user_id}')
async def remove_member(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    return await company_service.remove_member(company_id, user_id, current_user)
