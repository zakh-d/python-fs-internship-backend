from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.repositories.quizz_repository import QuizzRepository
from app.schemas.quizz_schema import (
    AnswerCreateSchema,
    AnswerSchema,
    AnswerUpdateSchema,
    AnswerWithCorrectSchema,
    QuestionCreateSchema,
    QuestionSchema,
    QuestionUpdateSchema,
    QuestionWithCorrectAnswerSchema,
    QuizzCreateSchema,
    QuizzListSchema,
    QuizzSchema,
    QuizzUpdateSchema,
    QuizzWithCorrectAnswersSchema,
    QuizzWithNoQuestionsSchema,
)
from app.services.quizz_service.exceptions import QuizzError, QuizzNotFound


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

    async def add_question_to_quizz(self, quizz_id: UUID, question_data: QuestionCreateSchema) -> None:
        async with self._quizz_repository.unit():
            question = await self._quizz_repository.create_question(
                text=question_data.text,
                quizz_id=quizz_id,
            )
            for answer_data in question_data.answers:
                await self._quizz_repository.create_answer(
                    **answer_data.model_dump(),
                    question_id=question.id
                )
    
    async def add_answer_to_question(self, quizz_id: UUID, question_id: UUID, answer_data: AnswerCreateSchema) -> None:
        question = await self._quizz_repository.get_question(question_id)
        if question.quizz_id != quizz_id:
            raise QuizzNotFound('Question')
        if await self._quizz_repository.get_question_answers_count(question_id) == 4:
            raise QuizzError('Question can have max 4 answers')
        await self._quizz_repository.create_answer(
            **answer_data.model_dump(),
            question_id=question_id
        )
        await self._quizz_repository.commit()
        

    async def get_quizz(self, quizz_id: UUID) -> QuizzWithNoQuestionsSchema:
        quizz = await self._quizz_repository.get_quizz(quizz_id)
        if not quizz:
            raise QuizzNotFound()
        return QuizzWithNoQuestionsSchema.model_validate(quizz)

    async def fetch_quizz_questions(self, quizz_without_questions: QuizzWithNoQuestionsSchema) -> QuizzSchema:
        quizz = QuizzSchema(**quizz_without_questions.model_dump(), questions=[])
        questions = await self._quizz_repository.get_quizz_questions(quizz.id)
        for question in questions:
            question_schema = QuestionSchema(id=question.id, text=question.text, answers=[])
            answers = await self._quizz_repository.get_question_answers(question.id)
            question_schema.answers = [AnswerSchema.model_validate(answer) for answer in answers]
            quizz.questions.append(question_schema)
        return quizz

    async def fetch_quizz_questions_with_correct_answers(
        self, quizz_without_questions: QuizzWithNoQuestionsSchema
    ) -> QuizzWithCorrectAnswersSchema:
        quizz = QuizzSchema(**quizz_without_questions.model_dump(), questions=[])
        questions = await self._quizz_repository.get_quizz_questions(quizz.id)
        for question in questions:
            question_schema = QuestionWithCorrectAnswerSchema(id=question.id, text=question.text, answers=[])
            answers = await self._quizz_repository.get_question_answers(question.id)
            question_schema.answers = [AnswerWithCorrectSchema.model_validate(answer) for answer in answers]
            quizz.questions.append(question_schema)
        return quizz

    async def get_company_quizzes(self, company_id: UUID, page: int, limit: int) -> QuizzListSchema:
        offset = (page - 1) * limit
        quizzes = await self._quizz_repository.get_company_quizzes(company_id, offset, limit)
        return QuizzListSchema(
            quizzes=[QuizzWithNoQuestionsSchema.model_validate(quizz) for quizz in quizzes],
            total_count=await self._quizz_repository.get_company_quizzes_count(company_id),
        )

    async def delete_quizz(self, quizz_id: UUID) -> None:
        await self._quizz_repository.delete_quizz(quizz_id)
    
    async def delete_question(self, question_id: UUID, quizz_id: UUID) -> None:
        if await self._quizz_repository.get_quizz_questions_count(quizz_id) < 2:
            raise QuizzError('Cannot delete last question')
        question = await self._quizz_repository.delete_question(question_id)
        if not question:
            raise QuizzNotFound('Question')
        if question.quizz_id != quizz_id:
            raise QuizzNotFound()
        await self._quizz_repository.delete_question(question_id)
    
    async def delete_answer(self, answer_id: UUID, quizz_id: UUID) -> None:
        answer = await self._quizz_repository.get_answer(answer_id)
        if not answer:
            raise QuizzNotFound('Answer')
        question = await self._quizz_repository.get_question(answer.question_id)
        if await self._quizz_repository.get_question_answers_count(question.id) < 3:
            raise QuizzError('Question must have at least two answer')
        if answer.is_correct:
            answers = await self._quizz_repository.get_question_answers(question.id)
            correct_answers = [answer for answer in answers if answer.is_correct]
            if len(correct_answers) < 2:
                raise QuizzError('Cannot delete only correct answer')
        if question.quizz_id != quizz_id:
            raise QuizzNotFound()
        await self._quizz_repository.delete_answer(answer_id)

    async def update_quizz(self, quizz_id: UUID, quizz_data: QuizzUpdateSchema) -> QuizzWithNoQuestionsSchema:
        quizz = await self._quizz_repository.get_quizz(quizz_id)
        if not quizz:
            raise QuizzNotFound()
        quizz = await self._quizz_repository.update_quizz(quizz, quizz_data)
        await self._quizz_repository.commit()
        return QuizzWithNoQuestionsSchema.model_validate(quizz)
    
    async def update_question(self, question_id: UUID, quizz_id: UUID, question_data: QuestionUpdateSchema) -> None:
        question = await self._quizz_repository.get_question(question_id)
        if not question:
            raise QuizzNotFound('Question')
        if question.quizz_id != quizz_id:
            raise QuizzNotFound('Question')
        await self._quizz_repository.update_question(question, question_data)
        await self._quizz_repository.commit()

    async def update_answer(self, answer_id: UUID, quizz_id: UUID, answer_data: AnswerUpdateSchema) -> None:
        answer = await self._quizz_repository.get_answer(answer_id)
        if not answer:
            raise QuizzNotFound('Answer')
        question = await self._quizz_repository.get_question(answer.question_id)
        if question.quizz_id != quizz_id:
            raise QuizzNotFound('Answer')
        if answer.is_correct and not answer_data.is_correct:
            answers = await self._quizz_repository.get_question_answers(question.id)
            correct_answers = [answer for answer in answers if answer.is_correct]
            if len(correct_answers) < 2:
                raise QuizzError('Question must have at least one correct answers')
        await self._quizz_repository.update_answer(answer, answer_data)
        await self._quizz_repository.commit()
