from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.company_action_schema import CompanyActionSchema
from app.schemas.company_schema import CompanyListSchema
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
from app.services.company_service.service import CompanyService
from app.utils.permissions import only_user_itself

router = APIRouter()


@router.get('/', response_model=UserList)
async def read_users(
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
    page: int = 1,
    limit: int = 10,
) -> UserList:
    return await user_service.get_all_users(page, limit)


@router.post('/', response_model=UserSchema)
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserSchema:
    return await user_service.create_user(user)


@router.get('/me', response_model=UserDetail)
async def read_me(
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(current_user.id)


@router.get('/{user_id}', response_model=UserDetail)
async def read_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}', response_model=UserDetail)
@only_user_itself
async def update_user(
    user_id: UUID,
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
    user: UserUpdateSchema,
    user_service: Annotated[UserService, Depends(UserService)],
) -> UserDetail:
    return await user_service.update_user(user_id, user)


@router.delete('/{user_id}')
@only_user_itself
async def delete_user(
    user_id: UUID,
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
    user_service: Annotated[UserService, Depends(UserService)],
) -> None:
    await user_service.delete_user(user_id)


@router.post('/sign_in')
async def sign_in(
    user_sign_in: UserSignInSchema, auth_service: Annotated[AuthenticationService, Depends(AuthenticationService)]
) -> dict[str, str]:
    user = await auth_service.authenticate(user_sign_in)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = auth_service.generate_jwt_token(user)
    return {'access_token': token}


@router.get('{user_id}/invites/')
async def get_invites_for_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> CompanyListSchema:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return await user_service.get_user_invites(user_id)


@router.post('{user_id}/invites/{company_id}')
async def accept_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await company_service.check_company_exists(company_id)
    await user_service.accept_invitation(user_id, company_id)


@router.delete('{user_id}/invites/{company_id}')
async def reject_invite_to_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await company_service.check_company_exists(company_id)
    await user_service.reject_invitation(user_id, company_id)


@router.get('{user_id}/requests/')
async def get_user_requests(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> CompanyListSchema:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return await user_service.get_user_requests(user_id)


@router.post('{user_id}/requests/{company_id}')
async def request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> CompanyActionSchema:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await company_service.check_company_exists(company_id)
    request = await user_service.send_request(user_id, company_id)
    return request


@router.delete('{user_id}/requests/{company_id}')
async def cancel_request_to_join_company(
    user_id: UUID,
    company_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    company_service: Annotated[CompanyService, Depends(CompanyService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await company_service.check_company_exists(company_id)
    await user_service.cancel_request(user_id, company_id)
