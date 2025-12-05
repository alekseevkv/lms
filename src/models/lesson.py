from typing import Any
from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModelMixin
from .course import Course


class Lesson(Base, BaseModelMixin):
    __tablename__ = "lessons"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Foreign key to course
    course_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("courses.uuid", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationship
    course: Mapped[Course] = relationship("Course", back_populates="lessons")

    def __repr__(self) -> str:
        return f"Lesson(uuid={self.uuid}, name={self.name!r}, course_id={self.course_id})"

    def to_dict(self, video_only: bool = False) -> dict[str, Any]:
        if video_only:
            return {
                "uuid": self.uuid,
                "name": self.name,
                "video_url": self.video_url,
                "course_id": self.course_id,
            }
        
        return {
            "uuid": self.uuid,
            "name": self.name,
            "desc": self.desc,
            "content": self.content,
            "video_url": self.video_url,
            "course_id": self.course_id,
        }