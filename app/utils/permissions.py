from functools import wraps
from uuid import UUID
from fastapi import HTTPException, status

from app.schemas.user_shema import UserDetail


def only_user_itself(func):

    @wraps(func)
    async def wrapper(user_id: UUID, current_user: UserDetail, *args, **kwargs):
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await func(user_id, current_user, *args, **kwargs)
    return wrapper
