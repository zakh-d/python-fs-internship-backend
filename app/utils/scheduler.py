from app.db.db import async_session
from app.repositories.notification_repository import NotificationRepository
from app.repositories.quizz_repository import QuizzRepository
from app.repositories.user_repository import UserRepository


async def check_quizz_completions() -> None:
    async with async_session() as session:
        quizz_repo = QuizzRepository(session)
        user_repo = UserRepository(session)
        notification_repo = NotificationRepository(session)

        users_count = await user_repo.get_users_count()
        users = await user_repo.get_all_users(0, users_count)
        for user in users:
            for overdued_quizz in await quizz_repo.get_users_overdued_quizzes(user.id):
                await notification_repo.create_notification_and_commit(
                    user_id=user.id,
                    title='Overdued quizz',
                    body=f'You have overdued quizz {overdued_quizz.title}'
                )
