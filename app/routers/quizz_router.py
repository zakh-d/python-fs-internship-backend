from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.quizz_schema import QuizzCreateSchema, QuizzSchema
from app.schemas.user_shema import UserDetail
from app.services.company_service.service import CompanyService
from app.services.quizz_service.service import QuizzService

router = APIRouter()


@router.post('/')
async def create_quizz(
    quizz_data: QuizzCreateSchema,
    company_service: Annotated[CompanyService, Depends()],
    quizz_service: Annotated[QuizzService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzSchema:
    await company_service.check_owner_or_admin(quizz_data.company_id, current_user.id)
    return await quizz_service.create_quizz(quizz_data, quizz_data.company_id)


@router.get('/{quizz_id}')
async def get_quizz(
    quizz_id: UUID,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzSchema:
    quizz_no_questions = await quizz_service.get_quizz(quizz_id)
    await company_service.check_is_member(quizz_no_questions.company_id, current_user.id)
    quizz_with_questions = await quizz_service.fetch_quizz_questions(quizz_no_questions)
    return quizz_with_questions
