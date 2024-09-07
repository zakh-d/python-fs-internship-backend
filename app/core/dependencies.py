from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.service import CompanyService
from app.services.notification_service.service import NotificationService
from app.services.quizz_service.service import QuizzService
from app.services.users_service.service import UserService


def get_user_service(session: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(session)


def get_quizz_service(session: Annotated[AsyncSession, Depends(get_db)]) -> QuizzService:
    return QuizzService(session)


def get_notification_service(session: Annotated[AsyncSession, Depends(get_db)]) -> NotificationService:
    return NotificationService(session)


def get_company_service(session: Annotated[AsyncSession, Depends(get_db)]) -> CompanyService:
    return CompanyService(session)


def get_authentication_service(session: Annotated[AsyncSession, Depends(get_db)]) -> AuthenticationService:
    return AuthenticationService(session)
