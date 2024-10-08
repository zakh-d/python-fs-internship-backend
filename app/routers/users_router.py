import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import get_authentication_service, get_company_service, get_quizz_service, get_user_service
from app.core.security import get_current_user
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import CompanyListSchema
from app.schemas.quizz_schema import (
    CompletionInfoSchema,
    QuizzResultAnalyticsListSchema,
    QuizzResultSchema,
)
from app.schemas.user_shema import (
    UserDetail,
    UserList,
    UserSchema,
    UserSignInSchema,
    UserSignUpSchema,
    UserUpdateSchema,
)
from app.services import UserService
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.exceptions import CompanyActionException
from app.services.company_service.service import CompanyService
from app.services.quizz_service.service import QuizzService
from app.utils.permissions import only_user_itself

router = APIRouter()


@router.get('/', response_model=UserList, dependencies=[Depends(get_current_user)])
async def read_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = 1,
    limit: int = 10,
) -> UserList:
    return await user_service.get_all_users(page, limit)


@router.post('/', response_model=UserSchema)
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserSchema:
    return await user_service.create_user(user)


@router.get('/me/', response_model=UserDetail)
async def read_me(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(current_user.id)


@router.get('/{user_id}/', response_model=UserDetail)
async def read_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}/', response_model=UserDetail, dependencies=[Depends(only_user_itself)])
async def update_user(
    user_id: UUID, user: UserUpdateSchema, user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserDetail:
    return await user_service.update_user(user_id, user)


@router.delete('/{user_id}/', dependencies=[Depends(only_user_itself)])
async def delete_user(user_id: UUID, user_service: Annotated[UserService, Depends(get_user_service)]) -> None:
    await user_service.delete_user(user_id)


@router.post('/sign_in/')
async def sign_in(
    user_sign_in: UserSignInSchema, auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)]
) -> dict[str, str]:
    user = await auth_service.authenticate(user_sign_in)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    token = auth_service.generate_jwt_token(user)
    return {'access_token': token}


@router.get('/{user_id}/invites/', dependencies=[Depends(only_user_itself)])
async def get_invites_for_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> CompanyListSchema:
    return await user_service.get_user_invites(user_id)


@router.post('/{user_id}/invites/{company_id}/', dependencies=[Depends(only_user_itself)])
async def accept_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.accept_invitation(user_id, company_id)


@router.delete('/{user_id}/invites/{company_id}/', dependencies=[Depends(only_user_itself)])
async def reject_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.reject_invitation(user_id, company_id)


@router.get('/{user_id}/requests/', dependencies=[Depends(only_user_itself)])
async def get_user_requests(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> CompanyListSchema:
    return await user_service.get_user_requests(user_id)


@router.post('/{user_id}/requests/{company_id}/', dependencies=[Depends(only_user_itself)])
async def request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyActionSchema:
    await company_service.check_company_exists_and_is_public(company_id)
    request = await user_service.send_request(user_id, company_id)
    return request


@router.delete('/{user_id}/requests/{company_id}/', dependencies=[Depends(only_user_itself)])
async def cancel_request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.cancel_request(user_id, company_id)


@router.get('/{user_id}/companies/', dependencies=[Depends(only_user_itself)])
async def get_user_companies(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> CompanyListSchema:
    return await user_service.get_user_companies(user_id)


@router.delete('/{user_id}/companies/{company_id}/', dependencies=[Depends(only_user_itself)])
async def leave_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyListSchema:
    company = await company_service.check_company_exists(company_id)
    if company.owner_id == user_id:
        raise CompanyActionException('Owner cannot leave company')
    return await user_service.leave_company(user_id, company_id)


@router.get('/{user_id}/quizzes/average/', tags=['quizzes', 'users'])
async def get_user_quizzes_average_score(
    user_id: UUID,
    quiz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> QuizzResultSchema:
    user = await user_service.get_user_by_id(user_id)
    return await quiz_service.get_average_score_by_user(user.id)


@router.get('/{user_id}/quizz_responses/', tags=['quizzes', 'users'], dependencies=[Depends(only_user_itself)])
async def get_user_quizz_responses(
    user_id: UUID,
    quiz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    format: Literal['json', 'csv'] = 'json',
) -> Response:
    if format == 'csv':
        return Response(content=await quiz_service.get_user_responses_from_cache_csv(user_id), media_type='text/csv')
    data = await quiz_service.get_user_responses_from_cache_json(user_id)
    return Response(content=data.model_dump_json(), media_type='text/json')


@router.get(
    '/{user_id}/quizzes/average/by/quizzes/', tags=['quizzes', 'users'], dependencies=[Depends(only_user_itself)]
)
async def get_user_average_score_by_quizzes(
    user_id: UUID,
    quiz_service: Annotated[QuizzService, Depends(get_quizz_service)],
    interval: Literal['days', 'weeks', 'months'] = 'weeks',
) -> list[QuizzResultAnalyticsListSchema]:
    if interval == 'days':
        return await quiz_service.get_average_score_for_user_by_quizzes_over_intervals(
            user_id, datetime.timedelta(days=1)
        )
    if interval == 'weeks':
        return await quiz_service.get_average_score_for_user_by_quizzes_over_intervals(
            user_id, datetime.timedelta(weeks=1)
        )
    return await quiz_service.get_average_score_for_user_by_quizzes_over_intervals(user_id, datetime.timedelta(weeks=4))


@router.get('/{user_id}/quizzes/latest/', tags=['quizzes', 'users'], dependencies=[Depends(only_user_itself)])
async def get_latest_quizz_completion_by_user(
    user_id: UUID,
    quiz_service: Annotated[QuizzService, Depends(get_quizz_service)],
) -> list[CompletionInfoSchema]:
    return await quiz_service.get_lastest_user_completions(user_id)
