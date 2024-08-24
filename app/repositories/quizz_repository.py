from typing import Literal, Optional, Union
from uuid import UUID

from sqlalchemy import and_, func, select

from app.db.models import Answer, Question, Quizz, QuizzResult
from app.redis import get_redis_client
from app.repositories.repository_base import RepositoryBase
from app.schemas.quizz_schema import (
    AnswerUpdateSchema,
    ChoosenAnswerSchema,
    QuestionResultSchema,
    QuestionUpdateSchema,
    QuizzDetailResultSchema,
    QuizzUpdateSchema,
)

ID_OR_MATCH_ALL = Union[UUID, Literal['*']]


class QuizzRepository(RepositoryBase):
    async def create_quizz(self, title: str, description: Optional[str], frequency: int, company_id: UUID) -> Quizz:
        quizz = Quizz(title=title, description=description, frequency=frequency, company_id=company_id)
        self.db.add(quizz)
        await self.db.flush()
        await self.db.refresh(quizz)
        return quizz

    async def create_question(self, text: str, quizz_id: UUID) -> Question:
        question = Question(text=text, quizz_id=quizz_id)
        self.db.add(question)
        await self.db.flush()
        await self.db.refresh(question)
        return question

    async def create_answer(self, text: str, question_id: UUID, is_correct: bool) -> Answer:
        answer = Answer(text=text, question_id=question_id, is_correct=is_correct)
        self.db.add(answer)
        await self.db.flush()
        await self.db.refresh(answer)
        return answer

    async def get_quizz(self, quizz_id: UUID) -> Union[Quizz, None]:
        return await self._get_item_by_id(quizz_id, Quizz)

    async def get_question(self, question_id: UUID) -> Union[Question, None]:
        return await self._get_item_by_id(question_id, Question)

    async def get_answer(self, answer_id: UUID) -> Union[Answer, None]:
        return await self._get_item_by_id(answer_id, Answer)

    async def get_company_quizzes(self, company_id: UUID, offset: int = 0, limit: int = 10) -> list[Quizz]:
        query = select(Quizz).where(Quizz.company_id == company_id).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_quizzes_count(self, company_id: UUID) -> int:
        query = select(func.count(Quizz.id)).where(Quizz.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_quizz_questions(self, quizz_id: UUID) -> list[Question]:
        query = select(Question).where(Question.quizz_id == quizz_id).order_by(Question.created_at)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_quizz_questions_count(self, quizz_id: UUID) -> int:
        query = select(func.count(Question.id)).where(Question.quizz_id == quizz_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_question_answers(self, question_id: UUID) -> list[Answer]:
        query = select(Answer).where(Answer.question_id == question_id).order_by(Answer.created_at)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_question_answers_count(self, question_id: UUID) -> int:
        query = select(func.count(Answer.id)).where(Answer.question_id == question_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def delete_quizz_and_commit(self, quizz_id: UUID) -> None:
        await self._delete_item_by_id(quizz_id, Quizz)
        await self.db.commit()

    async def delete_question_and_commit(self, question_id: UUID) -> None:
        await self._delete_item_by_id(question_id, Question)
        await self.db.commit()

    async def delete_answer_and_commit(self, answer_id: UUID) -> None:
        await self._delete_item_by_id(answer_id, Answer)
        await self.db.commit()

    async def update_quizz(self, quizz: Quizz, new_data: QuizzUpdateSchema) -> Quizz:
        for field in new_data.dict(exclude_unset=True):
            setattr(quizz, field, new_data.dict()[field])
        await self.db.flush()
        await self.db.refresh(quizz)
        return quizz

    async def update_question(self, question: Question, new_data: QuestionUpdateSchema) -> Question:
        for field in new_data.dict(exclude_unset=True):
            setattr(question, field, new_data.dict()[field])
        await self.db.flush()
        await self.db.refresh(question)
        return question

    async def update_answer(self, answer: Answer, new_data: AnswerUpdateSchema) -> Answer:
        for field in new_data.dict(exclude_unset=True):
            setattr(answer, field, new_data.dict()[field])
        await self.db.flush()
        await self.db.refresh(answer)
        return answer

    async def create_quizz_result(self, user_id: UUID, quizz_id: UUID, company_id: UUID, score: int) -> QuizzResult:
        quizz_result = QuizzResult(user_id=user_id, quizz_id=quizz_id, company_id=company_id, score=score)
        self.db.add(quizz_result)
        await self.db.flush()
        await self.db.refresh(quizz_result)
        return quizz_result

    async def get_latest_quizz_result(self, user_id: UUID, quizz_id: UUID) -> Union[QuizzResult, None]:
        query = (
            select(QuizzResult)
            .where(and_(QuizzResult.user_id == user_id, QuizzResult.quizz_id == quizz_id))
            .order_by(QuizzResult.created_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_average_score_by_company(self, company_id: UUID) -> float:
        query = select(func.avg(QuizzResult.score)).where(QuizzResult.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_average_score_by_user(self, user_id: UUID) -> float:
        query = select(func.avg(QuizzResult.score)).where(QuizzResult.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_average_score_by_quizz(self, quizz_id: UUID) -> float:
        query = select(func.avg(QuizzResult.score)).where(QuizzResult.quizz_id == quizz_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def cache_quizz_result(
        self, user_id: UUID, company_id: UUID, quizz_id: UUID, data: QuizzDetailResultSchema
    ) -> None:
        redis = await get_redis_client()
        _48_hours = 48 * 60 * 60
        async with redis.pipeline(transaction=True) as pipe:
            for question in data.questions:
                for answer in question.choosen_answers:
                    key = self._create_key(user_id, company_id, quizz_id, question.question_id, answer.answer_id)
                    pipe.set(key, 1 if answer.is_correct else 0, ex=_48_hours)

            await pipe.execute()
        await redis.close()
    
    async def delete_cached_quizz_for_user(self, user_id: UUID, quizz_id: UUID) -> None:
        redis = await get_redis_client()
        lookup_key = self._create_key(
            user_id=user_id,
            company_id='*',
            quizz_id=quizz_id,
            question_id='*',
            answer_id='*')
        keys = await redis.keys(lookup_key)
        if len(keys) > 0:
            await redis.delete(*keys)
        await redis.close()

    def _parse_key(self, key: str) -> tuple[UUID, UUID, UUID, UUID, UUID]:
        _, user_id, company_id, quizz_id, question_id, answer_id = key.split(':')
        return UUID(user_id), UUID(company_id), UUID(quizz_id), UUID(question_id), UUID(answer_id)

    def _create_key(
        self,
        user_id: ID_OR_MATCH_ALL,
        company_id: ID_OR_MATCH_ALL,
        quizz_id: ID_OR_MATCH_ALL,
        question_id: ID_OR_MATCH_ALL,
        answer_id: ID_OR_MATCH_ALL,
    ) -> str:
        return f'answer:{user_id}:{company_id}:{quizz_id}:{question_id}:{answer_id}'

    async def get_user_quizz_cache_keys(self, user_id: UUID, quizz_id: UUID) -> QuizzDetailResultSchema:
        redis = await get_redis_client()
        lookup_key = self._create_key(
            user_id=user_id,
            company_id='*',
            quizz_id=quizz_id,
            question_id='*',
            answer_id='*',
        )
        keys = await redis.keys(lookup_key)
        responses = await redis.mget(keys)
        keys = [key.decode() for key in keys]
        result = QuizzDetailResultSchema(questions=[])
        for key, response in zip(keys, responses):
            _, _, _, cached_question_id, cached_answer_id = self._parse_key(key)
            try:
                question_index = [q.question_id for q in result.questions].index(cached_question_id)
            except ValueError:
                result.questions.append(QuestionResultSchema(question_id=cached_question_id, choosen_answers=[]))
                question_index = len(result.questions) - 1
            result.questions[question_index].choosen_answers.append(
                ChoosenAnswerSchema(answer_id=cached_answer_id, is_correct=response == b'1')
            )
        await redis.close()
        return result
