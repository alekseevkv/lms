from typing import Any

from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base, BaseModelMixin


class TestQuestion(Base, BaseModelMixin):
    __tablename__ = "test_questions"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[dict[str,str]] = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    lesson_id: Mapped[str] = mapped_column(String, nullable=False)
    # когда появится урок
    # lesson_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("lesson.uuid", ondelete="SET NULL"),
    #     nullable=True,
    # )

    # lesson = relationship("Lesson", back_populates="test_questions")

    def __repr__(self) -> str:
        return (
            f"uuid - {self.uuid}, name - {self.name}, desc - {self.desc}, "
            f"question - {self.question}, choices - {self.choices}, "
            f"correct_answer - {self.correct_answer}, lesson_id - {self.lesson_id}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "desc": self.desc,
            "question": self.question,
            "choices": self.choices,
            "correct_answer": self.correct_answer,
            "lesson_id": self.lesson_id,
        }
