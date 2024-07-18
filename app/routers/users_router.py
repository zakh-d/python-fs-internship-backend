from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.user_shema import UserDetail, UserList, UserSchema, UserSignUpSchema, UserUpdateSchema
from app.services import UserService
from app.services.users_service.exceptions import (
    InvalidPasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
)

router = APIRouter()


@router.get('/')
async def read_users(user_service: Annotated[UserService, Depends(UserService)]) -> UserList:
    return await user_service.get_all_users()


@router.post('/sign_up/')
async def user_sign_up(
    user: UserSignUpSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserSchema:
    try:
        return await user_service.create_user(user)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{user_id}')
async def read_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)]) -> UserDetail:
    try:
        return await user_service.get_user_by_id(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put('/{user_id}')
async def update_user(
    user_id: UUID, user: UserUpdateSchema, user_service: Annotated[UserService, Depends(UserService)]
) -> UserDetail:
    try:
        return await user_service.update_user(user_id, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidPasswordException:
        raise HTTPException(status_code=401, detail='Invalid password')
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{user_id}')
async def delete_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)]) -> None:
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
