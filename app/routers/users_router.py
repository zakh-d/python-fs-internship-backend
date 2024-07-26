from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
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
