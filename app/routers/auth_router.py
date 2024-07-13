from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.schemas.user_shema import UserSignInSchema
from app.services.authentication_service import AuthenticationService


router = APIRouter()


@router.post("/sign_in")
async def sign_in(user_sign_in: UserSignInSchema, db: AsyncSession = Depends(get_db)):
    user = await AuthenticationService.authenticate(db, user_sign_in)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = AuthenticationService.generate_jwt_token(user)
    return {"token": token}
