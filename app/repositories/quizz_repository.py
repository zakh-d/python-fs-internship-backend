from typing import Optional, Union
from uuid import UUID

from sqlalchemy import func, select

from app.db.models import Answer, Question, Quizz
from app.repositories.repository_base import RepositoryBase


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
    
    async def get_company_quizzes(self, company_id: UUID, offset: int = 0, limit: int = 10) -> list[Quizz]:
        query = select(Quizz).where(Quizz.company_id == company_id).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_quizzes_count(self, company_id: UUID) -> int:
        query = select(func.count(Quizz.id)).where(Quizz.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def get_quizz_questions(self, quizz_id: UUID) -> list[Question]:
        query = select(Question).where(Question.quizz_id == quizz_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_question_answers(self, question_id: UUID) -> list[Answer]:
        query = select(Answer).where(Answer.question_id == question_id)
        result = await self.db.execute(query)
        return result.scalars().all()
