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
        default= list
    )
    # Связи
    user: Mapped[User] = relationship("User", back_populates="user_courses")
    course: Mapped[Course] = relationship("Course", back_populates="user_courses")

    def __repr__(self) -> str:
        return f"UserCourse(uuid={self.uuid}, user_id={self.user_id}, course_id={self.course_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "progress": self.progress,
            "create_at": self.create_at,
            "update_at": self.update_at,
        }
