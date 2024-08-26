from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.notification_schema import NotificationSchema
from app.schemas.user_shema import UserSchema
from app.services.notification_service.service import NotificationService

router = APIRouter()


@router.get('/')
async def get_user_notifications(
    notification_service: Annotated[NotificationService, Depends()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
) -> list[NotificationSchema]:
    return await notification_service.get_user_notifications(current_user.id)


@router.put('/{notification_id}/')
async def read_notification(
    notification_id: int,
    notification_service: Annotated[NotificationService, Depends()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
) -> NotificationSchema:
    return await notification_service.read_notification(notification_id, current_user.id)
