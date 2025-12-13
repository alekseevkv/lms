from typing import Any
from uuid import UUID

from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModelMixin


class Review(Base, BaseModelMixin):
    __tablename__ = "reviews"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("courses.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    course = relationship("Course", back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review(user_id={self.user_id!s}, course_id={self.course_id!s})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "content": self.content,
        }
