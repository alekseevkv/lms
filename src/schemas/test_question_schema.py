from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator, model_validator, ConfigDict
from typing import Optional, List, Annotated

def non_empty_str(v: str) -> str:
    if not v.strip():
            raise ValueError("String can't be empty")
    return v

NonEmptyStr = Annotated[str, Field(min_length=1), BeforeValidator(non_empty_str)]
PositiveInt = Annotated[int, Field(gt=0)]


class TestQuestionBase(BaseModel):
    question_num: PositiveInt
    desc: Optional[str] = None
    question: NonEmptyStr
    choices: List[NonEmptyStr]
    lesson_id: UUID

class TestQuestionCreate(TestQuestionBase):
    correct_answer: NonEmptyStr
    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode='after')
    def validate_answer(self) -> 'TestQuestionCreate':
        if self.correct_answer.strip() not in [choice.strip() for choice in self.choices]:
            raise ValueError(f"Answer {self.correct_answer} must be among the choices {self.choices}")
        return self


class TestQuestionUpdate(BaseModel):
    question_num: Optional[PositiveInt] = None
    desc: Optional[str] = None
    question: Optional[NonEmptyStr] = None
    choices: Optional[List[NonEmptyStr]] = None
    correct_answer: Optional[NonEmptyStr] = None
    lesson_id: Optional[UUID] = None


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
    user_answer: NonEmptyStr


class LessonAnswer(BaseModel):
    user_answers: List[TestQuestionAnswer]


class CheckAnswerResponse(BaseModel):
    uuid: UUID
    passed: bool
    correct_answer: str


class CheckAnswerListResponse(BaseModel):
    checked_answers: List[CheckAnswerResponse]
    message: Optional[str] = None
    already_answered: Optional[List[UUID]] = None
    new_questions_answered: Optional[List[UUID]] = None
    error_message: Optional[str] = None


class LessonEstimateResponse(BaseModel):
    lesson_id: UUID
    percentage: float


class TestQuestionCount(BaseModel):
    total: int


class TestQuestionsCountByLesson(BaseModel):
    lesson_id: UUID
    total: int