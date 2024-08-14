from typing import Optional
from uuid import UUID

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
