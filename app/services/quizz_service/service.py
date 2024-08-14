from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.repositories.quizz_repository import QuizzRepository
from app.schemas.quizz_schema import QuizzCreateSchema


class QuizzService:

    def __init__(self, quizz_repository: Annotated[QuizzRepository, Depends()]) -> None:
        self._quizz_repository = quizz_repository

    async def create_quizz(self, quizz_data: QuizzCreateSchema, company_id: UUID) -> None:

        async with self._quizz_repository.unit():
            quizz = await self._quizz_repository.create_quizz(
                title=quizz_data.title,
                description=quizz_data.description,
                frequency=quizz_data.frequency,
                company_id=company_id,
            )
            for question_data in quizz_data.questions:
                question = await self._quizz_repository.create_question(
                    text=question_data.text,
                    quizz_id=quizz.id,
                )
                for answer_data in question_data.answers:
                    self._quizz_repository.create_answer(
                        text=answer_data.text,
                        question_id=question.id,
                        is_correct=answer_data.is_correct,
                    )
            return quizz_data
