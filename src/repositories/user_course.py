from collections.abc import Sequence
from typing import Any, Dict, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.user_course import UserCourse, UserLessonProgress
from src.models.course import Course
from src.models.lesson import Lesson
from src.models.user import User


class UserCourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_course_id: UUID) -> UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.uuid == user_course_id,
                UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_course(
        self, user_id: UUID, course_id: UUID
    ) -> UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == course_id,
                UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: UUID, skip: int | None = 0, limit: int | None = 100
    ) -> Sequence[UserCourse]:
        result = await self.db.execute(
            select(UserCourse)
            .where(UserCourse.user_id == user_id, UserCourse.archived == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, user_course_data: dict) -> UserCourse:
        user_course = UserCourse(**user_course_data)
        self.db.add(user_course)
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course

    async def update(self, user_course_id: UUID, update_data: dict) -> UserCourse | None:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None

        for key, value in update_data.items():
            setattr(user_course, key, value)

        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course

    async def delete(self, user_course_id: UUID) -> UserCourse | None:
        user_course = await self.get_by_id(user_course_id)
        if user_course:
            user_course.archived = True
            await self.db.commit()
            await self.db.refresh(user_course)
        return user_course

    async def get_lesson_progress(
        self, user_course_id: UUID, lesson_id: UUID
    ) -> UserLessonProgress | None:
        result = await self.db.execute(
            select(UserLessonProgress).where(
                UserLessonProgress.user_course_id == user_course_id,
                UserLessonProgress.lesson_id == lesson_id
            )
        )
        return result.scalar_one_or_none()

    async def start_lesson(
        self, user_course_id: UUID, lesson_id: UUID
    ) -> UserLessonProgress:
        # Проверяем, есть ли уже прогресс
        progress = await self.get_lesson_progress(user_course_id, lesson_id)
        
        if not progress:
            # Создаем новую запись
            progress = UserLessonProgress(
                user_course_id=user_course_id,
                lesson_id=lesson_id,
                started=True
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)
        elif not progress.started:
            # Обновляем существующую запись
            progress.started = True
            await self.db.commit()
            await self.db.refresh(progress)
        
        return progress

    async def complete_lesson(
        self, user_course_id: UUID, lesson_id: UUID, estimate: float | None = None
    ) -> UserLessonProgress:
        progress = await self.get_lesson_progress(user_course_id, lesson_id)
        
        if not progress:
            # Создаем новую запись как завершенную
            progress = UserLessonProgress(
                user_course_id=user_course_id,
                lesson_id=lesson_id,
                started=True,
                completed=True,
                estimate=estimate
            )
            self.db.add(progress)
        else:
            # Обновляем существующую запись
            progress.started = True
            progress.completed = True
            progress.estimate = estimate
        
        await self.db.commit()
        await self.db.refresh(progress)
        
        # Обновляем общий прогресс курса
        user_course = await self.get_by_id(user_course_id)
        if user_course:
            # Получаем все уроки курса
            result = await self.db.execute(
                select(Lesson).where(Lesson.course_id == user_course.course_id)
            )
            all_lessons = result.scalars().all()
            
            # Получаем завершенные уроки
            result = await self.db.execute(
                select(UserLessonProgress).where(
                    UserLessonProgress.user_course_id == user_course_id,
                    UserLessonProgress.completed == True
                )
            )
            completed_lessons = result.scalars().all()
            
            # Обновляем прогресс
            if all_lessons:
                user_course.total_progress = (len(completed_lessons) / len(all_lessons)) * 100
                await self.db.commit()
                await self.db.refresh(user_course)
        
        return progress

    async def get_course_with_progress(self, user_course_id: UUID) -> Dict:
        # Получаем UserCourse с курсом и уроками
        result = await self.db.execute(
            select(UserCourse, Course, Lesson)
            .join(Course, UserCourse.course_id == Course.uuid)
            .outerjoin(Lesson, Course.uuid == Lesson.course_id)
            .where(
                UserCourse.uuid == user_course_id,
                UserCourse.archived == False,
                Lesson.archived == False
            )
        )
        rows = result.all()
        
        if not rows:
            return None
        
        user_course = rows[0].UserCourse
        course = rows[0].Course
        
        # Собираем уроки с их прогрессом
        lessons_with_progress = []
        for row in rows:
            if row.Lesson:
                lesson = row.Lesson
                # Получаем прогресс по уроку
                progress = await self.get_lesson_progress(user_course_id, lesson.uuid)
                
                lessons_with_progress.append({
                    "uuid": lesson.uuid,
                    "name": lesson.name,
                    "desc": lesson.desc,
                    "content": lesson.content,
                    "video_url": lesson.video_url,
                    "course_id": lesson.course_id,
                    "progress": {
                        "started": progress.started if progress else False,
                        "completed": progress.completed if progress else False,
                        "estimate": progress.estimate if progress else None
                    }
                })
        
        return {
            "user_course": user_course,
            "course": course,
            "lessons": lessons_with_progress
        }


async def get_user_course_repository(
    db: AsyncSession = Depends(get_session),
) -> UserCourseRepository:
    return UserCourseRepository(db)