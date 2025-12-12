from .base import Base, BaseModelMixin

from .course import Course
from .test_question import TestQuestion
from .user import User
from .lesson import Lesson
from .review import Review
from .user_course import UserCourse
__all__ = ["Base", "BaseModelMixin", "Course", "Lesson", "TestQuestion", "User", "Review", "UserCourse"]
