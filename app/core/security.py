from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user_shema import UserDetail
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
        token: Annotated[str, Depends(get_token_from_header)],
        auth_service: Annotated[AuthenticationService, Depends(AuthenticationService)]
        ) -> UserDetail:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await auth_service.get_user_by_token(token)

    if user is None:
        raise credentials_exception

    return user
