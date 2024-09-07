from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationSchema
from app.services.notification_service.exceptions import CannotSendNotificationException, NotificationNotFound


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._notification_repository = NotificationRepository(session)
        self._company_respository = CompanyRepository(session)
        self._company_action_respository = CompanyActionRepository(session)

    async def get_user_notifications(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[NotificationSchema]:
        notifications = await self._notification_repository.get_user_notifications(user_id, limit, offset)
        return [NotificationSchema.model_validate(notification) for notification in notifications]

    async def send_notification_to_user(self, to_user_id: UUID, title: str, body: str) -> NotificationSchema:
        notification = await self._notification_repository.create_notification_and_commit(to_user_id, title, body)
        if notification is None:
            raise CannotSendNotificationException()
        return NotificationSchema.model_validate(notification)

    async def send_notification_to_company_members(self, company_id: UUID, title: str, body: str) -> None:
        comapny = await self._company_respository.get_company_by_id(company_id)
        if comapny is None:
            raise CannotSendNotificationException()
        members = await self._company_action_respository.get_users_related_to_company(
            company_id, CompanyActionType.MEMBERSHIP
        )
        for member in members:
            await self.send_notification_to_user(member.id, title, body)

    async def read_notification(self, notification_id: UUID, user_id: UUID) -> NotificationSchema:
        notification = await self._notification_repository.get_notification_by_id(notification_id)
        if notification is None:
            raise NotificationNotFound(notification_id)
        if notification.user_id != user_id:
            raise NotificationNotFound(notification_id)
        notification = await self._notification_repository.read_notification_and_commit(notification)
        return NotificationSchema.model_validate(notification)
