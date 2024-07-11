from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.schemas.user_shema import UserDetail, UserSchema, UserSignUpSchema, UserList, UserUpdateSchema
from app.services import UserService
from app.services.users_service.exceptions import InvalidPasswordException, UserNotFoundException

router = APIRouter()


@router.get("/")
async def read_users(db: AsyncSession = Depends(get_db)) -> UserList:
    return await UserService.get_all_users(db)


@router.post("/sign_up/")
async def user_sign_up(user: UserSignUpSchema, db: AsyncSession = Depends(get_db)) -> UserSchema:
    return await UserService.create_user(db, user)


@router.get("/{user_id}")
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserDetail:
    try:
        return await UserService.get_user_by_id(db, user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: UUID, user: UserUpdateSchema, db: AsyncSession = Depends(get_db)) -> UserDetail:
    try:
        return await UserService.update_user(db, user_id, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidPasswordException:
        raise HTTPException(status_code=401, detail='Invalid password')
