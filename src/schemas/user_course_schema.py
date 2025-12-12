from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, field_validator


class LessonProgress(BaseModel):
    lesson_id: UUID
    estimate: float  # Процент правильных ответов (0-100)

    @field_validator('estimate')
    @classmethod
    def validate_estimate(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError('Estimate must be between 0 and 100')
        return v


class UserCourseBase(BaseModel):
    course_id: UUID
    progress: List[Dict[str, Any]] = []


class UserCourseCreate(UserCourseBase):
    pass


class UserCourseUpdate(BaseModel):
    progress: Optional[List[Dict[str, Any]]] = None


class UserCourseProgressUpdate(BaseModel):
    lesson_id: UUID
    estimate: float


class UserCourseResponse(BaseModel):
    uuid: UUID
    user_id: UUID
    course_id: UUID
    progress: List[Dict[str, Any]]
    create_at: datetime
    update_at: datetime

    model_config = {"from_attributes": True}


class CourseWithProgressResponse(BaseModel):
    """Курс с информацией о прогрессе пользователя"""
    course_id: UUID
    course_name: str
    course_description: Optional[str] = None
    total_lessons: int
    completed_lessons: int
    overall_progress: float  # Общий прогресс в процентах


class LessonWithProgress(BaseModel):
    lesson: Dict[str, Any]
    progress: Optional[Dict[str, Any]] = None


class UserCourseDetailResponse(BaseModel):
    """Детальная информация о курсе пользователя"""
    user_course: UserCourseResponse
    course: Dict[str, Any]
    lessons_with_progress: List[LessonWithProgress]


class UserCourseListResponse(BaseModel):
    """Список курсов пользователя с прогрессом"""
    user_courses: List[CourseWithProgressResponse]


class StartLessonResponse(BaseModel):
    """Ответ при начале прохождения урока"""
    lesson_id: UUID
    lesson_name: str
    message: str = "Lesson started successfully"