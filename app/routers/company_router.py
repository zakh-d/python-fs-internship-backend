from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.company_schema import CompanyCreateSchema, CompanyListSchema, CompanySchema
from app.schemas.user_shema import UserDetail
from app.services.company_service.service import CompanyService

router = APIRouter()


@router.get("/")
async def get_companies(
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    _: Annotated[UserDetail, Depends(get_current_user)]  # requires authentication
) -> CompanyListSchema:
    return await company_service.get_all_companies()


@router.get("/{company_id}")
async def get_company_by_id(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    _: Annotated[UserDetail, Depends(get_current_user)]  # requires authentication
) -> CompanySchema:
    return await company_service.get_company_by_id(company_id)


@router.post("/")
async def create_company(
    company_data: CompanyCreateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)]
) -> CompanySchema:
    return await company_service.create_company(company_data, current_user)


@router.put("/{company_id}")
async def update_company(
    company_id: UUID,
    company_data: CompanyCreateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(CompanyService)]
) -> CompanySchema:
    return await company_service.update_company(company_id, company_data, current_user)
