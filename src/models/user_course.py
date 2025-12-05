from typing import Any, List, Dict
from uuid import UUID as PyUUID
import json

from sqlalchemy import ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .base import Base, BaseModelMixin
from .user import User
from .course import Course
from .lesson import Lesson

class UserCourse(Base, BaseModelMixin):
    __tablename__ = "user_courses"

    user_id: Mapped[PyUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False
    )
    course_id: Mapped[PyUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("courses.uuid", ondelete="CASCADE"),
        nullable=False
    )
    progress: Mapped[Dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"lessons": []}
    )
    total_progress: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="user_courses")
    course: Mapped["Course"] = relationship("Course", back_populates="user_courses")

    def __repr__(self) -> str:
        return f"UserCourse(uuid={self.uuid}, user_id={self.user_id}, course_id={self.course_id}, progress={self.total_progress})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "progress": self.progress,
            "total_progress": self.total_progress,
            "create_at": self.create_at,
            "update_at": self.update_at,
        }
    
    def update_progress(self) -> None:
        """Обновляет общий прогресс на основе завершенных уроков"""
        lessons = self.progress.get("lessons", [])
        if not lessons:
            self.total_progress = 0.0
            return
        
        completed_lessons = sum(1 for lesson in lessons if lesson.get("estimate") is not None)
        self.total_progress = (completed_lessons / len(lessons)) * 100


class UserLessonProgress(Base, BaseModelMixin):
    __tablename__ = "user_lesson_progress"
    
    user_course_id: Mapped[PyUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_courses.uuid", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )
    lesson_id: Mapped[PyUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lessons.uuid", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )
    started: Mapped[bool] = mapped_column(default=False)
    completed: Mapped[bool] = mapped_column(default=False)
    estimate: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Связи
    user_course: Mapped["UserCourse"] = relationship("UserCourse")
    lesson: Mapped["Lesson"] = relationship("Lesson")
    
    def __repr__(self) -> str:
        return f"UserLessonProgress(user_course_id={self.user_course_id}, lesson_id={self.lesson_id}, estimate={self.estimate})"