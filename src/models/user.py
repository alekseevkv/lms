from enum import Enum
from typing import Any

from sqlalchemy import ARRAY, Column, String

from .base import Base, BaseModelMixin


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    username = Column(String)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False, default=lambda: [])

    def __repr__(self) -> str:
        return (
            f"uuid - {self.uuid}, username - {self.username}"
            f"email - {self.email}, roles - {self.roles}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "username": self.username,
            "email": self.email,
            "roles": self.roles,
        }
