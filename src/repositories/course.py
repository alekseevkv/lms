from collections.abc import Sequence
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.course import Course


class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, course_id: Any) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.uuid == course_id))

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.name == name))

        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        course = await self.get_by_name(name)
        return course is not None

    async def get_all(
        self, skip: int | None = 0, limit: int | None = 100
    ) -> Sequence[Course]:
        result = await self.db.execute(select(Course).offset(skip).limit(limit))

        return result.scalars().all()


async def get_course_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseRepository:
    return CourseRepository(db)
