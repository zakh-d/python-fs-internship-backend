from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.user_shema import UserDetail, UserSignInSchema
from app.services.authentication_service import AuthenticationService


router = APIRouter()


@router.post("/sign_in")
async def sign_in(
    user_sign_in: UserSignInSchema,
    auth_service: Annotated[AuthenticationService, Depends(AuthenticationService)]
) -> dict[str, str]:
    user = await auth_service.authenticate(user_sign_in)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = AuthenticationService.generate_jwt_token(user)
    return {"access_token": token}


@router.get('/me')
async def get_me(current_user: Annotated[UserDetail, Depends(get_current_user)]) -> UserDetail:
    return current_user
