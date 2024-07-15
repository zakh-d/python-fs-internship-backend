from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.db import get_db
from app.schemas.user_shema import UserSchema, UserSignInSchema
from app.services.authentication_service import AuthenticationService


router = APIRouter()


@router.post("/sign_in")
async def sign_in(user_sign_in: UserSignInSchema, db: AsyncSession = Depends(get_db)):
    user = await AuthenticationService.authenticate(db, user_sign_in)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = AuthenticationService.generate_jwt_token(user)
    return {"access_token": token}


@router.post('/me')
async def get_me(current_user: Annotated[UserSchema, Depends(get_current_user)]) -> UserSchema:
    return current_user
