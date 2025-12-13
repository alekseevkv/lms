from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, List


class TestQuestionBase(BaseModel):
    question_num: int
    desc: Optional[str] = None
    question: str
    choices: List[str]
    lesson_id: UUID

    @field_validator('question_num')
    @classmethod
    def validate_num(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Question number must be larger than 0')
        return v


class TestQuestionCreate(TestQuestionBase):
    correct_answer: str


class TestQuestionUpdate(BaseModel):
    question_num: Optional[int] = None
    desc: Optional[str] = None
    question: Optional[str] = None
    choices: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    lesson_id: Optional[UUID] = None

    @field_validator('question_num')
    @classmethod
    def validate_num(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Question number must be larger than 0')
        return v


class TestQuestionWithoutAnswerResponse(TestQuestionBase):
    uuid: UUID
    model_config = {"from_attributes": True}


class TestQuestionWithoutAnswerListResponse(BaseModel):
    questions_list: list[TestQuestionWithoutAnswerResponse]
    skip: int
    limit: int


class TestQuestionResponse(TestQuestionWithoutAnswerResponse):
    correct_answer: str
    create_at: datetime
    update_at: datetime
    archived: bool


class TestQuestionListResponse(BaseModel):
    questions_list: list[TestQuestionResponse]
    total: int | None
    skip: int
    limit: int


class TestQuestionAnswer(BaseModel):
    uuid: UUID
    user_answer: str


class LessonAnswer(BaseModel):
    user_answers: List[TestQuestionAnswer]


class CheckAnswerResponse(BaseModel):
    uuid: UUID
    passed: bool
    correct_answer: str


class CheckAnswerListResponse(BaseModel):
    checked_answers: List[CheckAnswerResponse]


class LessonEstimateResponse(BaseModel):
    lesson_id: UUID
    percentage: float


class TestQuestionCount(BaseModel):
    total: int


class TestQuestionsCountByLesson(BaseModel):
    lesson_id: UUID
    total: int