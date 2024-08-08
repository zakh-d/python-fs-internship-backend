from typing import Annotated, TypeVar
from uuid import UUID

from fastapi import Depends, HTTPException, status
from typing_extensions import ParamSpec

from app.core.security import get_current_user
from app.schemas.user_shema import UserDetail

Param = ParamSpec('Param')
RetType = TypeVar('RetType')


def only_user_itself(user_id: UUID, current_user: Annotated[UserDetail, Depends(get_current_user)]) -> None:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
