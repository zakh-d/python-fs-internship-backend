from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.schemas.user_shema import UserSchema, UserSignUpSchema, UserList
from app.services import UserService

router = APIRouter()


@router.get("/")
async def read_users(db: AsyncSession = Depends(get_db)) -> UserList:
    return await UserService.get_all_users(db)


@router.post("/sign_up/")
async def user_sign_up(user: UserSignUpSchema, db: AsyncSession = Depends(get_db)) -> UserSchema:
    return await UserService.create_user(db, user)
