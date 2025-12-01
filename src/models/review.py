from typing import Any

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseModelMixin


class Review(Base, BaseModelMixin):
    __tablename__ = "reviews"

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"Review(user_id={self.user_id!r}, course_id={self.course_id!r})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "content": self.content,
        }
