from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user_shema import UserSchema


async def get_all_users(db: AsyncSession) -> list[UserSchema]:
    users = await User.get_all_users(db)
    return [UserSchema.model_validate(user) for user in users]
