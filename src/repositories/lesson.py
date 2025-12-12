from collections.abc import Sequence
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.lesson import Lesson


class LessonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, lesson_id: Any) -> Lesson | None:
        result = await self.db.execute(
            select(Lesson).where(Lesson.uuid == lesson_id, Lesson.archived == False)
        )
        return result.scalar_one_or_none()

    async def get_all_by_course(
        self, course_id: Any, skip: int | None = 0, limit: int | None = 100
    ) -> Sequence[Lesson]:
        result = await self.db.execute(
            select(Lesson)
            .where(Lesson.course_id == course_id, Lesson.archived == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def exists_by_name_in_course(self, name: str, course_id: Any) -> bool:
        result = await self.db.execute(
            select(Lesson).where(
                Lesson.name == name,
                Lesson.course_id == course_id,
                Lesson.archived == False
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, lesson_data: dict) -> Lesson:
        lesson = Lesson(**lesson_data)
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def update(self, lesson_id: Any, update_data: dict) -> Lesson | None:
        lesson = await self.get_by_id(lesson_id)
        if not lesson:
            return None

        for key, value in update_data.items():
            setattr(lesson, key, value)

        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def delete(self, lesson_id: Any) -> Lesson | None:
        lesson = await self.get_by_id(lesson_id)
        if lesson:
            lesson.archived = True
            await self.db.commit()
            await self.db.refresh(lesson)
        return lesson


async def get_lesson_repository(
    db: AsyncSession = Depends(get_session),
) -> LessonRepository:
    return LessonRepository(db)