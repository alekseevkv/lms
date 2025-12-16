from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, field_validator

class QuestionProgress(BaseModel):
    """Прогресс по одному вопросу"""
    question_id: UUID
    estimate: float  # Оценка за конкретный вопрос (0 или 100)

    @field_validator('estimate')
    @classmethod
    def validate_estimate(cls, v: float) -> float:
        if v not in (0, 100):
            raise ValueError('Question estimate must be 0 (wrong) or 100 (correct)')
        return v


class LessonProgress(BaseModel):
    """Прогресс по одному уроку"""
    lesson_id: UUID
    questions: List[QuestionProgress]  # Список прогресса по вопросам
    
    def calculate_percentage(self) -> float:
        """Рассчитать процент правильных ответов для урока"""
        if not self.questions:
            return 0.0
        correct_answers = sum(1 for q in self.questions if q.estimate == 100)
        return (correct_answers / len(self.questions)) * 100



class UserCourseBase(BaseModel):
    course_id: UUID
    progress: List[Dict[str, Any]] = []


class UserCourseCreate(UserCourseBase):
    pass


class UserCourseUpdate(BaseModel):
    progress: Optional[List[Dict[str, Any]]] = None


class UserCourseProgressUpdate(BaseModel):
    """Обновление прогресса по уроку с детализацией по вопросам"""
    lesson_id: UUID
    question_progress: List[QuestionProgress]  # Прогресс по каждому вопросу
    
    def to_dict_format(self) -> Dict[str, Any]:
        """Преобразовать в формат для хранения в БД"""
        return {
            "lesson_id": str(self.lesson_id),
            "questions": [
                {
                    "question_id": str(qp.question_id),
                    "estimate": qp.estimate
                }
                for qp in self.question_progress
            ]
        }
        
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
    user_course_id: UUID


class LessonWithProgress(BaseModel):
    lesson: Dict[str, Any]
    progress: Optional[Dict[str, Any]] = None

class LessonProgressDetail(BaseModel):
    """Детализированный прогресс по уроку для get_user_course_detail"""
    lesson_id: UUID
    lesson_name: str
    started: bool
    completed: bool
    questions: Optional[List[Dict[str, Any]]] = None
    estimate: Optional[float] = None

class UserCourseDetailResponse(BaseModel):
    """Ответ для get_user_course_detail"""
    user_id: UUID
    course_id: UUID
    course_name: str
    progress_for_lessons: List[LessonProgressDetail]


class UserCourseListResponse(BaseModel):
    """Список курсов пользователя с прогрессом"""
    user_courses: List[CourseWithProgressResponse]


class StartLessonResponse(BaseModel):
    """Ответ при начале прохождения урока"""
    lesson_id: UUID
    lesson_name: str
    message: str = "Lesson started successfully"
    


