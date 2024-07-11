from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.schemas.user_shema import UserSignUpSchema
from app.services import UserService

router = APIRouter()


@router.get("/users/")
async def read_users(db: AsyncSession = Depends(get_db)):
    return await UserService.get_all_users(db)


@router.post("/users/sign_up/")
async def user_sign_up(user: UserSignUpSchema, db: AsyncSession = Depends(get_db)):
    await UserService.create_user(db, user)
    return {"message": "User created successfully"}
