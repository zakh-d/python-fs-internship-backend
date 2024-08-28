from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import CompanyListSchema
from app.schemas.quizz_schema import QuizzResultSchema
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
    user_service: Annotated[UserService, Depends(UserService)],
    page: int = 1,
    limit: int = 10,
) -> UserList:
    return await user_service.get_all_users(page, limit)


@router.post('/', response_model=UserSchema)
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserSchema:
    return await user_service.create_user(user)


@router.get('/me/', response_model=UserDetail)
async def read_me(
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(current_user.id)


@router.get('/{user_id}/', response_model=UserDetail)
async def read_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}/', response_model=UserDetail, dependencies=[Depends(only_user_itself)])
async def update_user(
    user_id: UUID, user: UserUpdateSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserDetail:
    return await user_service.update_user(user_id, user)


@router.delete('/{user_id}/', dependencies=[Depends(only_user_itself)])
async def delete_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)]) -> None:
    await user_service.delete_user(user_id)


@router.post('/sign_in/')
async def sign_in(
    user_sign_in: UserSignInSchema, auth_service: Annotated[AuthenticationService, Depends(AuthenticationService)]
) -> dict[str, str]:
    user = await auth_service.authenticate(user_sign_in)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = auth_service.generate_jwt_token(user)
    return {'access_token': token}


@router.get('/{user_id}/invites/', dependencies=[Depends(only_user_itself)])
async def get_invites_for_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
) -> CompanyListSchema:
    return await user_service.get_user_invites(user_id)


@router.post('/{user_id}/invites/{company_id}/', dependencies=[Depends(only_user_itself)])
async def accept_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.accept_invitation(user_id, company_id)


@router.delete('/{user_id}/invites/{company_id}/', dependencies=[Depends(only_user_itself)])
async def reject_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.reject_invitation(user_id, company_id)


@router.get('/{user_id}/requests/', dependencies=[Depends(only_user_itself)])
async def get_user_requests(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
) -> CompanyListSchema:
    return await user_service.get_user_requests(user_id)


@router.post('/{user_id}/requests/{company_id}/', dependencies=[Depends(only_user_itself)])
async def request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanyActionSchema:
    await company_service.check_company_exists_and_is_public(company_id)
    request = await user_service.send_request(user_id, company_id)
    return request


@router.delete('/{user_id}/requests/{company_id}/', dependencies=[Depends(only_user_itself)])
async def cancel_request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> None:
    await company_service.check_company_exists(company_id)
    await user_service.cancel_request(user_id, company_id)


@router.get('/{user_id}/companies/', dependencies=[Depends(only_user_itself)])
async def get_user_companies(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
) -> CompanyListSchema:
    return await user_service.get_user_companies(user_id)


@router.delete('/{user_id}/companies/{company_id}/', dependencies=[Depends(only_user_itself)])
async def leave_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
) -> CompanyListSchema:
    company = await company_service.check_company_exists(company_id)
    if company.owner_id == user_id:
        raise CompanyActionException('Owner cannot leave company')
    return await user_service.leave_company(user_id, company_id)


@router.get('/{user_id}/quizzes/average/', tags=['quizzes', 'users'])
async def get_user_quizzes_average_score(
    user_id: UUID,
    quiz_service: Annotated[QuizzService, Depends()],
    user_service: Annotated[UserService, Depends()],
) -> QuizzResultSchema:
    user = await user_service.get_user_by_id(user_id)
    return await quiz_service.get_average_score_by_user(user.id)
