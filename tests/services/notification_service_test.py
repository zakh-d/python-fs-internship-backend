import uuid
from fastapi import HTTPException
import pytest

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.user_shema import UserSchema
from app.services.notification_service import NotificationService
from app.services.notification_service.exceptions import CannotSendNotificationException


@pytest.mark.asyncio
async def test_send_notification(test_user: UserSchema, notification_service: NotificationService, notification_repo: NotificationRepository):
    
    await notification_service.send_notification_to_user(test_user.id, 'Test title', 'Test body')
    notifications = await notification_repo.get_user_notifications(test_user.id)
    
    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_send_notification_to_non_existing_user(notification_service: NotificationService):
    with pytest.raises(HTTPException):
        await notification_service.send_notification_to_user(uuid.uuid4(), 'Test title', 'Test body')


@pytest.mark.asyncio
async def test_send_notification_to_company_members(notification_service: NotificationService, company_and_users, company_action_repo: CompanyActionRepository):
    company, owner, user = company_and_users
    company_action_repo.create(company.id, user.id, CompanyActionType.MEMBERSHIP)
    await company_action_repo.commit()

    await notification_service.send_notification_to_company_members(company.id, 'Test title', 'Test body')
    notifications = await notification_service.get_user_notifications(owner.id)
    
    assert len(notifications) == 1
    assert notifications[0].title == 'Test title'
    assert notifications[0].body == 'Test body'

    notifications = await notification_service.get_user_notifications(user.id)
    
    assert len(notifications) == 1
    assert notifications[0].title == 'Test title'
    assert notifications[0].body == 'Test body'


@pytest.mark.asyncio
async def test_send_notifications_to_members_of_non_existing_company(notification_service: NotificationService):
    with pytest.raises(CannotSendNotificationException):
        await notification_service.send_notification_to_company_members(uuid.uuid4(), 'Test title', 'Test body')
