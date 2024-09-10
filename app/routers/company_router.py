import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import get_company_service, get_quizz_service, get_user_service
from app.core.security import get_current_user
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    CompanyDetailWithIsMemberSchema,
    CompanyListSchema,
    CompanySchema,
    CompanyUpdateSchema,
)
from app.schemas.quizz_schema import (
    QuizzListSchema,
    QuizzResultSchema,
    QuizzResultsListForDateSchema,
)
from app.schemas.user_shema import UserDetail, UserEmailSchema, UserIdSchema, UserInCompanyList, UserList
from app.services.company_service.service import CompanyService
from app.services.quizz_service.service import QuizzService
from app.services.users_service.service import UserService

router = APIRouter()


@router.get('/')
async def get_companies(
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
    page: int = 1,
    limit: int = 10,
) -> CompanyListSchema:
    return await company_service.get_all_companies(page, limit)


@router.get('/my/')
async def get_my_companies(
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> CompanyListSchema:
    return await company_service.get_companies_user_is_part_of(current_user.id)


@router.get('/{company_id}')
async def get_company_by_id(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> CompanyDetailWithIsMemberSchema:
    return await company_service.get_company_by_id(company_id, current_user)


@router.post('/')
async def create_company(
    company_data: CompanyCreateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanySchema:
    return await company_service.create_company(company_data, current_user)


@router.put('/{company_id}')
async def update_company(
    company_id: UUID,
    company_data: CompanyUpdateSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyDetailSchema:
    return await company_service.update_company(company_id, company_data, current_user)


@router.delete('/{company_id}')
async def delete_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> None:
    return await company_service.delete_company(company_id, current_user)


@router.get('/{company_id}/role/')
async def get_user_role_in_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> Literal['owner', 'admin', 'member', 'none']:
    return await company_service.get_user_role_in_company(company_id, current_user.id)


@router.get('/{company_id}/invites/')
async def get_invites_for_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> UserList:
    return await company_service.get_invites_for_company(company_id, current_user)


@router.post('/{company_id}/invites/')
async def intive_user_to_company(
    company_id: UUID,
    user_data: UserEmailSchema,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyActionSchema:
    user = await user_service.get_user_by_email(user_data.email)
    return await company_service.invite_user(company_id, user.id, current_user)


@router.delete('/{company_id}/invites/{user_id}')
async def cancel_invite(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    return await company_service.cancel_invite(company_id, user_id, current_user)


@router.get('/{company_id}/requests/')
async def get_requests_to_company(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],  # requires authentication
) -> UserList:
    return await company_service.get_requests_to_company(company_id, current_user)


@router.post('/{company_id}/requests/{user_id}')
async def accept_request(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyActionSchema:
    return await company_service.accept_request(company_id, user_id, current_user)


@router.delete('/{company_id}/requests/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def reject_request(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    return await company_service.reject_request(company_id, user_id, current_user)


@router.get('/{company_id}/members/', dependencies=[Depends(get_current_user)])
async def get_company_members(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> UserInCompanyList:
    return await company_service.get_company_members(company_id)


@router.delete('/{company_id}/members/{user_id}')
async def remove_member(
    company_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    return await company_service.remove_member(company_id, user_id, current_user)


@router.get('/{company_id}/admins/')
async def get_admin_list(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> UserList:
    return await company_service.get_admin_list(company_id, current_user)


@router.post('/{company_id}/admins/')
async def add_admin(
    company_id: UUID,
    user_schema: UserIdSchema,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> CompanyActionSchema:
    return await company_service.add_admin(company_id, user_schema.user_id, current_user)


@router.delete('/{company_id}/admins/{user_id}')
async def remove_admin(
    company_id: UUID,
    user_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> CompanyActionSchema:
    return await company_service.remove_admin(company_id, user_id, current_user)


@router.get('/{company_id}/quizzes/', tags=['quizzes', 'companies'])
async def get_company_quizzes(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    quizz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    page: int = 1,
    limit: int = 10,
) -> QuizzListSchema:
    await company_service.check_is_member(company_id, current_user.id)
    return await quizz_service.get_company_quizzes(company_id, page, limit)


@router.get('/{company_id}/quizzes/average/', tags=['quizzes', 'companies'])
async def get_company_quizzes_average(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    quizz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzResultSchema:
    await company_service.check_is_member(company_id, current_user.id)
    return await quizz_service.get_average_score_by_company(company_id)


@router.get('/{company_id}/quizzes/responses/{user_id}/', tags=['quizzes', 'companies'])
async def get_user_responses_for_company_quizzes(
    company_id: UUID,
    user_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    quizz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    format: Literal['json', 'csv'] = 'json',
) -> Response:
    await company_service.check_is_member(company_id, current_user.id)
    if format == 'csv':
        return Response(
            content=await quizz_service.get_user_responses_in_company_from_cache_csv(user_id, company_id),
            media_type='text/csv',
        )
    data = await quizz_service.get_user_responses_in_company_from_cache_json(user_id, company_id)
    return Response(content=data.model_dump_json(), media_type='text/json')


@router.get('/{company_id}/quizzes/responses/', tags=['quizzes', 'companies'])
async def get_all_members_responses_for_company_quizzes(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    quizz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    format: Literal['json', 'csv'] = 'json',
) -> Response:
    await company_service.check_owner_or_admin(company_id, current_user.id)
    if format == 'csv':
        return Response(
            content=await quizz_service.get_company_members_responses_from_cache_csv(company_id),
            media_type='text/csv',
        )
    data = await quizz_service.get_company_members_responses_from_cache_json(company_id)
    return Response(content=data.model_dump_json(), media_type='text/json')


@router.get('/{company_id}/quizzes/average/members/', tags=['quizzes', 'companies'])
async def get_company_members_average_score(
    company_id: UUID,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    quizz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    interval: Literal['days', 'weeks', 'months'] = 'weeks',
) -> list[QuizzResultsListForDateSchema]:
    await company_service.check_owner_or_admin(company_id, current_user.id)
    if interval == 'days':
        return await quizz_service.get_average_scores_for_company_members_over_intervals(
            company_id, datetime.timedelta(days=1)
        )
    elif interval == 'weeks':
        return await quizz_service.get_average_scores_for_company_members_over_intervals(
            company_id, datetime.timedelta(weeks=1)
        )
    return await quizz_service.get_average_scores_for_company_members_over_intervals(
        company_id,
        datetime.timedelta(weeks=4),  # 4 weeks in a month
    )
