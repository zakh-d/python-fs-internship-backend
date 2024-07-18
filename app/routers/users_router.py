from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.user_shema import UserDetail, UserList, UserSchema, UserSignUpSchema, UserUpdateSchema
from app.services import UserService

router = APIRouter()


@router.get('/')
async def read_users(user_service: Annotated[UserService, Depends(UserService)]) -> UserList:
    return await user_service.get_all_users()


@router.post('/sign_up/')
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserSchema:
    return await user_service.create_user(user)


@router.get('/{user_id}')
async def read_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)]) -> UserDetail:
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}')
async def update_user(
    user_id: UUID, user: UserUpdateSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserDetail:
    return await user_service.update_user(user_id, user)


@router.delete('/{user_id}')
async def delete_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)]) -> None:
    await user_service.delete_user(user_id)
