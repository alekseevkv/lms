from typing import Any, List
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, ARRAY, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base, BaseModelMixin
from .lesson import Lesson


class TestQuestion(Base, BaseModelMixin):
    __tablename__ = "test_questions"

    question_num: Mapped[int] = mapped_column(Integer, nullable=False)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lessons.uuid", ondelete="CASCADE"),
        nullable=False
    )
    lesson: Mapped[Lesson] = relationship("Lesson", back_populates="test_questions")

    def __repr__(self) -> str:
        return (
            f"uuid - {self.uuid}, question_num - {self.question_num}, desc - {self.desc}, "
            f"question - {self.question}, choices - {self.choices}, "
            f"correct_answer - {self.correct_answer}, lesson_id - {self.lesson_id}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "question_num": self.question_num,
            "desc": self.desc,
            "question": self.question,
            "choices": self.choices,
            "correct_answer": self.correct_answer,
            "lesson_id": self.lesson_id,
        }
