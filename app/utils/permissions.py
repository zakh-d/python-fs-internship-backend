from functools import wraps
from typing import Callable, TypeVar
from typing_extensions import ParamSpec
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.user_shema import UserDetail

Param = ParamSpec('Param')
RetType = TypeVar('RetType')


def only_user_itself(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
    @wraps(func)
    async def wrapper(user_id: UUID, current_user: UserDetail, *args, **kwargs) -> RetType:
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await func(user_id, current_user, *args, **kwargs)

    return wrapper
