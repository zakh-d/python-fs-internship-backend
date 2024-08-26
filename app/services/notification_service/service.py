from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.repositories.notification_reposotory import NotificationRepository
from app.schemas.notification_schema import NotificationSchema
from app.services.notification_service.exceptions import NotificationNotFound


class NotificationService:
    def __init__(self, notification_repository: Annotated[NotificationRepository, Depends()]) -> None:
        self._notification_repository = notification_repository

    async def get_user_notifications(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[NotificationSchema]:
        notifications = await self._notification_repository.get_user_notifications(user_id, limit, offset)
        return [NotificationSchema.model_validate(notification) for notification in notifications]

    async def send_notification(self, to_user_id: UUID, title: str, body: str) -> NotificationSchema:
        notification = await self._notification_repository.create_notification_and_commit(to_user_id, title, body)
        return NotificationSchema.model_validate(notification)

    async def read_notification(self, notification_id: int, user_id: UUID) -> NotificationSchema:
        notification = await self._notification_repository.get_notification_by_id(notification_id)
        if notification.user_id != user_id:
            raise NotificationNotFound(notification_id)
        notification.is_read = True
        self._notification_repository.commit()
        return NotificationSchema.model_validate(notification)
