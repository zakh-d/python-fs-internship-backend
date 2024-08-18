from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.quizz_schema import (
    AnswerCreateSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuizzCompletionSchema,
    QuizzCreateSchema,
    QuizzResultSchema,
    QuizzSchema,
    QuizzUpdateSchema,
    QuizzWithCorrectAnswersSchema,
    QuizzWithNoQuestionsSchema,
)
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


@router.get('/{quizz_id}/')
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


@router.put('/{quizz_id}/')
async def update_quizz(
    quizz_id: UUID,
    quizz_data: QuizzUpdateSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithNoQuestionsSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    return await quizz_service.update_quizz(quizz_id, quizz_data)


@router.get('/{quizz_id}/correct/')
async def get_quizz_with_correct_answers(
    quizz_id: UUID,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz_no_questions = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz_no_questions.company_id, current_user.id)
    quizz_with_questions = await quizz_service.fetch_quizz_questions_with_correct_answers(quizz_no_questions)
    return quizz_with_questions


@router.delete('/{quizz_id}/')
async def delete_quizz(
    quizz_id: UUID,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> None:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.delete_quizz(quizz_id)


@router.delete('/{quizz_id}/question/{question_id}/')
async def delete_question(
    quizz_id: UUID,
    question_id: UUID,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.delete_question(question_id, quizz_id)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.put('/{quizz_id}/question/{question_id}/')
async def update_question(
    quizz_id: UUID,
    question_id: UUID,
    question_data: QuestionUpdateSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.update_question(question_id, quizz_id, question_data)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.post('/{quizz_id}/question/')
async def add_question_to_quizz(
    quizz_id: UUID,
    question_data: QuestionCreateSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.add_question_to_quizz(quizz_id, question_data)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.post('/{quizz_id}/question/{question_id}/answer/')
async def add_answer_to_question(
    quizz_id: UUID,
    question_id: UUID,
    answer_data: AnswerCreateSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.add_answer_to_question(quizz_id, question_id, answer_data)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.delete('/{quizz_id}/answer/{answer_id}/')
async def delete_answer(
    quizz_id: UUID,
    answer_id: UUID,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.delete_answer(answer_id, quizz_id)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.put('/{quizz_id}/answer/{answer_id}/')
async def update_answer(
    quizz_id: UUID,
    answer_id: UUID,
    answer_data: AnswerCreateSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzWithCorrectAnswersSchema:
    quizz = await quizz_service.get_quizz(quizz_id)
    await company_service.check_owner_or_admin(quizz.company_id, current_user.id)
    await quizz_service.update_answer(answer_id, quizz_id, answer_data)
    return await quizz_service.fetch_quizz_questions_with_correct_answers(quizz)


@router.post('/complete/')
async def complete_quizz(
    quizz_completion_data: QuizzCompletionSchema,
    quizz_service: Annotated[QuizzService, Depends()],
    company_service: Annotated[CompanyService, Depends()],
    current_user: Annotated[UserDetail, Depends(get_current_user)],
) -> QuizzResultSchema:
    quizz = await quizz_service.get_quizz(quizz_completion_data.quizz_id)
    await company_service.check_is_member(quizz.company_id, current_user.id)
    return await quizz_service.evaluate_quizz(quizz, quizz_completion_data, current_user)
