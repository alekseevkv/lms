from typing import Any, List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModelMixin
#from .user_course import UserCourse
#from .lesson import Lesson

class Course(Base, BaseModelMixin):
    __tablename__ = "courses"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)

    lessons: Mapped[List["Lesson"]] = relationship( # noqa: F821 во избежание циклической зависимости
        "Lesson", 
        back_populates="course",
        cascade="all, delete-orphan"
        )
    
    
    # Добавляем relationship к UserCourse
    user_courses: Mapped[List["UserCourse"]] = relationship(  # noqa: F821
        "UserCourse",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    reviews: Mapped[List["Review"]] = relationship(  # noqa: F821
        "Review",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Course(uuid={self.uuid}, name={self.name!r}, desc={self.desc!r})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "desc": self.desc,
        }
