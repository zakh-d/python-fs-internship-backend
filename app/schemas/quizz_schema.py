from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self


class AnswerCreateSchema(BaseModel):
    text: str = Field(max_length=250)
    is_correct: bool


class QuestionCreateSchema(BaseModel):

    @model_validator(mode='after')
    def check_answers_number(self) -> Self:
        if len(self.answers) < 2 or len(self.answers) > 4:
            raise ValueError('question must have at min 2 and at max 4 answers')
        return self
    
    @model_validator(mode='after')
    def check_at_least_one_answer_is_correct(self) -> Self:
        if not any(answer.is_correct for answer in self.answers):
            raise ValueError('question must have at least one correct answer')
        return self

    text: str = Field(max_length=250)
    answers: list[AnswerCreateSchema]


class QuizzCreateSchema(BaseModel):

    @model_validator(mode='after')
    def check_at_least_one_question(self) -> Self:
        if not self.questions:
            raise ValueError('quizz must have at least one question')
        return self

    company_id: UUID
    title: str = Field(max_length=50)
    description: Optional[str] = Field(max_length=250, default=None)
    questions: list[QuestionCreateSchema]
    frequency: int


class AnswerSchema(BaseModel):
    id: UUID
    text: str
    
    model_config = ConfigDict(from_attributes=True)


class AnswerWithCorrectSchema(AnswerSchema):
    is_correct: bool


class QuestionSchema(BaseModel):
    id: UUID
    text: str
    answers: list[AnswerSchema]


class QuestionWithCorrectAnswerSchema(QuestionSchema):
    answers: list[AnswerWithCorrectSchema]


class QuizzWithNoQuestionsSchema(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    frequency: int
    company_id: UUID

    model_config = ConfigDict(from_attributes=True)


class QuizzSchema(QuizzWithNoQuestionsSchema):
    questions: list[QuestionSchema]

    model_config = ConfigDict(from_attributes=False)


class QuizzWithCorrectAnswersSchema(QuizzSchema):
    questions: list[QuestionWithCorrectAnswerSchema]

    model_config = ConfigDict(from_attributes=False)


class QuizzListSchema(BaseModel):
    quizzes: list[QuizzWithNoQuestionsSchema]
    total_count: int


class AnswerUpdateSchema(BaseModel):
    text: str = Field(max_length=250)
    is_correct: bool


class QuestionUpdateSchema(BaseModel):
    text: str = Field(max_length=250)


class QuizzUpdateSchema(BaseModel):
    title: str = Field(max_length=50)
    description: Optional[str] = Field(max_length=250, default=None)
    frequency: int
