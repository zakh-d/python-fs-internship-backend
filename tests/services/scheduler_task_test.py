import pytest

from app.repositories.notification_repository import NotificationRepository
from app.repositories.quizz_repository import QuizzRepository
from app.utils.scheduler import check_quizz_completions


@pytest.mark.asyncio
async def test_get_overdued_quizzes(
    test_quizz,
    company_and_users,
    quizz_repo: QuizzRepository
):
    company, owner, _ = company_and_users
    assert company.id == test_quizz.company_id

    overdue_quizzes = await quizz_repo.get_users_overdued_quizzes(owner.id)
    assert len(overdue_quizzes) == 1


@pytest.mark.asyncio
async def test_check_quizz_completions(
    get_db,
    test_quizz,
    company_and_users,
    notification_repo: NotificationRepository
):
    company, owner, _ = company_and_users
    assert company.id == test_quizz.company_id
    await check_quizz_completions(get_db)
    notifications = await notification_repo.get_user_notifications(owner.id)
    assert 'You have overdued quizz Test quizz' in [n.body for n in notifications]
