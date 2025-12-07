from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class LessonProgress(BaseModel):
    lesson_id: UUID
    estimate: Optional[float] = Field(None, ge=0, le=100)


class UserCourseBase(BaseModel):
    course_id: UUID


class UserCourseCreate(UserCourseBase):
    pass


class UserCourseProgress(BaseModel):
    lessons: List[LessonProgress] = []


class UserCourseResponse(BaseModel):
    uuid: UUID
    user_id: UUID
    course_id: UUID
    progress: UserCourseProgress
    total_progress: float = Field(ge=0, le=100)
    create_at: datetime
    update_at: datetime

    model_config = {"from_attributes": True}


class CourseWithProgressResponse(BaseModel):
    uuid: UUID
    name: str
    desc: Optional[str]
    user_progress: UserCourseResponse


class LessonWithProgress(BaseModel):
    uuid: UUID
    name: str
    desc: Optional[str]
    content: str
    video_url: Optional[str]
    course_id: UUID
    progress: Dict[str, Any]


class UserCourseDetailedResponse(BaseModel):
    user_course: UserCourseResponse
    course: Dict[str, Any]
    lessons: List[LessonWithProgress]


class StartLessonResponse(BaseModel):
    lesson: LessonWithProgress
    started: bool = True


class CompleteLessonRequest(BaseModel):
    estimate: Optional[float] = Field(None, ge=0, le=100)