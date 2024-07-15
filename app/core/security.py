from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user_shema import UserSchema
from app.services.authentication_service.service import AuthenticationService


security = HTTPBearer()


def get_token_from_header(authorization: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if authorization.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return authorization.credentials


async def get_current_user(
        token: str = Depends(get_token_from_header),
        db: AsyncSession = Depends(get_db)
        ) -> UserSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = AuthenticationService.get_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return UserSchema.model_validate(user)
