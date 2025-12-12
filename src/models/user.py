from typing import Any, List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModelMixin
#from .user_course import UserCourse

class User(Base, BaseModelMixin):
    __tablename__ = "users"

    username: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    roles: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    
    user_courses: Mapped[List["UserCourse"]] = relationship(  # noqa: F821
        "UserCourse",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return (
            f"User(uuid={self.uuid}, username={self.username}, "
            f"email={self.email}, roles={self.roles})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "username": self.username,
            "email": self.email,
            "roles": self.roles,
        }
