from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.quizz_repository import QuizzRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service.service import NotificationService


async def check_quizz_completions(session: AsyncSession) -> None:
    quizz_repo = QuizzRepository(session)
    user_repo = UserRepository(session)
    notification_service = NotificationService(session)

    users_count = await user_repo.get_users_count()
    users = await user_repo.get_all_users(0, users_count)
    for user in users:
        for overdued_quizz in await quizz_repo.get_users_overdued_quizzes(user.id):
            await notification_service.send_notification_to_user(
                to_user_id=user.id, title='Overdued quizz', body=f'You have overdued quizz {overdued_quizz.title}'
            )
