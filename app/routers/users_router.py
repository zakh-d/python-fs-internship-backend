from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.services.users_service import get_all_users

router = APIRouter()


@router.get("/users/")
async def read_users(db: AsyncSession = Depends(get_db)):
    return await get_all_users(db)
