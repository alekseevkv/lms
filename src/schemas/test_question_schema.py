from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class TestQuestionBase(BaseModel):
    name: str
    desc: Optional[str] = None
    question: str
    choices: List[str]
    correct_answer: str
    lesson_id: UUID


class TestQuestionCreate(TestQuestionBase):
    pass


class TestQuestionUpdate(TestQuestionBase):
    name: Optional[str] = None
    desc: Optional[str] = None
    question: Optional[str] = None
    choices: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    lesson_id: Optional[UUID] = None


class TestQuestionResponse(TestQuestionBase):
    uuid: UUID
    model_config = {"from_attributes": True}


class TestQuestionListResponse(BaseModel):
    test_questions: list[TestQuestionResponse]
    total: int
    skip: int
    limit: int


class TestQuestionWithoutAnswerResponse(TestQuestionBase):
    uuid: UUID
    model_config = ConfigDict(
        from_attributes=True, exclude={"correct_answer", "updated_at", "created_at", "archived"}
    )


class TestQuestionWithoutAnswerListResponse(BaseModel):
    test_questions: list[TestQuestionWithoutAnswerResponse]
    total: int
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


class LessonEstimateResponse(BaseModel):
    lesson_id: UUID
    percentage: float


class TestQuestionCount(BaseModel):
    total: int


class TestQuestionsCountByLesson(BaseModel):
    lesson_id: UUID
    total: int


class TestQuestionSearchParams(BaseModel):
    name_pattern: str
    skip: int = 0
    limit: int = 100
