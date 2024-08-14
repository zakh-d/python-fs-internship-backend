from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.repositories.quizz_repository import QuizzRepository
from app.schemas.quizz_schema import AnswerSchema, QuestionSchema, QuizzCreateSchema, QuizzSchema


class QuizzService:

    def __init__(self, quizz_repository: Annotated[QuizzRepository, Depends()]) -> None:
        self._quizz_repository = quizz_repository

    async def create_quizz(self, quizz_data: QuizzCreateSchema, company_id: UUID) -> QuizzSchema:
        async with self._quizz_repository.unit():
            quizz = await self._quizz_repository.create_quizz(
                title=quizz_data.title,
                description=quizz_data.description,
                frequency=quizz_data.frequency,
                company_id=company_id,
            )
            response_schema = QuizzSchema(
                **quizz_data.model_dump(exclude={'questions'}),
                questions=[],
                id=quizz.id,
            )
            for question_data in quizz_data.questions:
                question = await self._quizz_repository.create_question(
                    text=question_data.text,
                    quizz_id=quizz.id,
                )
                question_response_schema = QuestionSchema(
                    **question_data.model_dump(exclude={'answers'}),
                    answers=[],
                    id=question.id,
                )
                
                for answer_data in question_data.answers:
                    answer = await self._quizz_repository.create_answer(
                        text=answer_data.text,
                        question_id=question.id,
                        is_correct=answer_data.is_correct,
                    )
                    question_response_schema.answers.append(AnswerSchema.model_validate(answer))
                response_schema.questions.append(question_response_schema)
            return response_schema

    async def get_quizz(self, quizz_id: UUID) -> QuizzSchema:
        quizz = await self._quizz_repository.get_quizz(quizz_id)
        response_schema = QuizzSchema(
            id=quizz.id,
            title=quizz.title,
            description=quizz.description,
            frequency=quizz.frequency,
            company_id=quizz.company_id,
            questions=[]
        )
        return response_schema

    async def fetch_quizz_questions(self, quizz: QuizzSchema) -> QuizzSchema:
        questions = await self._quizz_repository.get_quizz_questions(quizz.id)

        for question in questions:
            question_schema = QuestionSchema(
                id=question.id,
                text=question.text,
                answers=[]
            )
            answers = await self._quizz_repository.get_question_answers(question.id)
            question_schema.answers = [AnswerSchema.model_validate(answer) for answer in answers]
            quizz.questions.append(question_schema)
        return quizz
 