from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.company_schema import CompanyCreateSchema, CompanyListSchema, CompanySchema, CompanyUpdateSchema
from app.schemas.invitation_request_schema import InvitationOrRequestCreateSchema
from app.schemas.user_shema import UserDetail
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


@router.get('/{company_id}')
async def get_company_by_id(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    _: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> CompanySchema:
    return await company_service.get_company_by_id(company_id)


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
) -> CompanySchema:
    return await company_service.update_company(company_id, company_data, current_user)


@router.delete('/{company_id}')
async def delete_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> None:
    return await company_service.delete_company(company_id, current_user)


@router.post('/invite')
async def intive_user_to_company(
    invite_data: InvitationOrRequestCreateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)]
) -> InvitationOrRequestCreateSchema:
    return await company_service.create_invitation_for_user(invite_data, current_user)
