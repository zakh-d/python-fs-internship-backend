from collections.abc import Sequence
from typing import Union
from uuid import UUID

from sqlalchemy import select

from app.db.models import Notification
from app.repositories.repository_base import RepositoryBase


class NotificationRepository(RepositoryBase):
    async def get_user_notifications(self, user_id: UUID, limit: int = 50, offset: int = 0) -> Sequence[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        results = await self.db.execute(query)
        return results.scalars().all()

    async def get_notification_by_id(self, notification_id: UUID) -> Union[Notification, None]:
        return await self._get_item_by_id(notification_id, Notification)
    
    async def read_notification(self, notification: Notification) -> Notification:
        self.db.add(notification)
        notification.is_read = True
        await self.db.commit()
        return notification

    def create_notification(self, user_id: UUID, title: str, body: str) -> Notification:
        notification = Notification(user_id=user_id, title=title, body=body, is_read=False)
        self.db.add(notification)
        return notification

    async def create_notification_and_commit(self, user_id: UUID, title: str, body: str) -> Union[Notification, None]:
        notification = self.create_notification(user_id, title, body)
        try:
            await self.commit()
            await self.db.refresh(notification)
            return notification
        except Exception:
            return None
