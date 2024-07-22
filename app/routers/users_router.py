from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.user_shema import UserDetail, UserList, UserSchema, UserSignUpSchema, UserUpdateSchema
from app.services import UserService

router = APIRouter()


@router.get('/', response_model=UserList)
async def read_users(
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserList:
    return await user_service.get_all_users()


@router.post('/sign_up/', response_model=UserSchema)
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserSchema:
    return await user_service.create_user(user)


@router.get('/{user_id}', response_model=UserDetail)
async def read_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(user_id)


@router.get('/me', response_model=UserDetail)
async def read_me(
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.get_user_by_id(current_user.id)


@router.put('/me', response_model=UserDetail)
async def update_me(
    user: UserUpdateSchema,
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> UserDetail:
    return await user_service.update_user(current_user.id, user)


@router.delete('/me')
async def delete_me(
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],  # requires authentication
) -> None:
    await user_service.delete_user(current_user.id)
