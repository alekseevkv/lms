from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List, Dict


class TestQuestionBase(BaseModel):
    name: str
    desc: Optional[str] = None
    question: str
    choices: Dict[str,str]
    lesson_id: str
    # lesson_id: UUID


class TestQuestionCreate(TestQuestionBase):
    correct_answer: str


class TestQuestionUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    question: Optional[str] = None
    choices: Optional[dict[str,str]] = None
    correct_answer: Optional[str] = None
    lesson_id: Optional[str] = None
    # lesson_id: Optional[UUID] = None


class TestQuestionWithoutAnswerResponse(TestQuestionBase):
    uuid: UUID
    model_config = {"from_attributes": True}


class TestQuestionWithoutAnswerListResponse(BaseModel):
    questions_list: list[TestQuestionWithoutAnswerResponse]
    skip: int
    limit: int


class TestQuestionResponse(TestQuestionWithoutAnswerResponse):
    correct_answer: str


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
    lesson_id: str
    # lesson_id: UUID
    percentage: float


class TestQuestionCount(BaseModel):
    total: int


class TestQuestionsCountByLesson(BaseModel):
    lesson_id: str
    # lesson_id: UUID
    total: int


class TestQuestionSearchParams(BaseModel):
    name_pattern: str
    skip: int = 0
    limit: int = 100
