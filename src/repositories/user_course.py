from collections.abc import Sequence
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.user_course import UserCourse
from src.models.course import Course
from src.models.lesson import Lesson
from src.models.user import User


class UserCourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_course_id: UUID) -> Optional[UserCourse]: #UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.uuid == user_course_id,
                #UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_course(self, user_id: UUID, course_id: UUID) -> Optional[UserCourse]:  #UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == course_id,
                #UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: UUID
        #, skip: int | None = 0, limit: int | None = 100
        #)-> Sequence[UserCourse]:
        )-> List[UserCourse]:
        result = await self.db.execute(
            select(UserCourse)
            .where(UserCourse.user_id == user_id,
                #UserCourse.archived == False
                )
            #.offset(skip)
            #.limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_course_data: Dict[str, Any]) -> UserCourse:
        user_course = UserCourse(**user_course_data)
        self.db.add(user_course)
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course

    #async def update(self, user_course: UserCourse) -> UserCourse:
    #    await self.db.commit()
    #    await self.db.refresh(user_course)
    #    return user_course
    
    
    async def update(self, user_course_id: UUID, update_data: Dict[str, Any]) -> Optional[UserCourse]:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None

        for key, value in update_data.items():
            setattr(user_course, key, value)

        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course
    
    
    async def update_progress(
        self, 
        user_course_id: UUID, 
        lesson_id: UUID, 
        estimate: float
    ) -> Optional[UserCourse]:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None

        # Ищем существующую запись об уроке
       # #progress_list = user_course.progress or []
        # SQLAlchemy JSON тип возвращает список/словарь
        #progress_list: List[Dict[str, Any]] = user_course.progress or []
        #lesson_id_str = str(lesson_id)
        #lesson_found = False
        
        #for i, item in enumerate(progress_list):
        #    if item.get("lesson_id") == str(lesson_id):
        #        progress_list[i]["estimate"] = estimate
        #        lesson_found = True
        #        break
        
        
        
        
        
        # Явно преобразуем прогресс в список словарей
        # Используем cast для подсказки типу
        current_progress = user_course.progress
        if not isinstance(current_progress, list):
            current_progress = []
        
        # Создаем новый список для избежания проблем с типами
        progress_list: List[Dict[str, Any]] = []
        
        # Копируем существующий прогресс
        for item in current_progress:
            if isinstance(item, dict):
                progress_list.append(dict(item))
        
        lesson_id_str = str(lesson_id)
        lesson_found = False
        
        for i, item in enumerate(progress_list):
            # Получаем lesson_id из прогресса
            progress_lesson_id = item.get("lesson_id")
            
            # Приводим к строке для сравнения
            if isinstance(progress_lesson_id, UUID):
                progress_lesson_id = str(progress_lesson_id)
            elif not isinstance(progress_lesson_id, str):
                continue
            
            if progress_lesson_id == lesson_id_str:
                # Обновляем существующую запись
                new_item = dict(item)
                new_item["estimate"] = estimate
                progress_list[i] = new_item
                lesson_found = True
                break
        # Если урок не найден, добавляем новую запись
        if not lesson_found:
            progress_list.append({
                "lesson_id": str(lesson_id),
                "estimate": estimate
            })
        setattr(user_course, 'progress', progress_list)
        #or
        #user_course.progress = progress_list #type: ignore
        
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course
   
    

    ##async def get_course_with_lessons(self, user_course_id: UUID) -> Dict:
        """Получить курс пользователя со всеми уроками и прогрессом"""
        # Получаем UserCourse
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.uuid == user_course_id,
                UserCourse.archived == False
            )
        )
        user_course = result.scalar_one_or_none()
        
        if not user_course:
            return None
        
        # Получаем курс
        result = await self.db.execute(
            select(Course).where(Course.uuid == user_course.course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            return None
        
        # Получаем все уроки курса
        result = await self.db.execute(
            select(Lesson).where(
                Lesson.course_id == course.uuid,
                Lesson.archived == False
            )
        )
        lessons = result.scalars().all()
        
        # Собираем уроки с их прогрессом
        lessons_with_progress = []
        for lesson in lessons:
            lesson_progress = user_course.get_lesson_progress(lesson.uuid)
            
            lessons_with_progress.append({
                "uuid": lesson.uuid,
                "name": lesson.name,
                "desc": lesson.desc,
                "content": lesson.content,
                "video_url": lesson.video_url,
                "course_id": lesson.course_id,
                "progress": {
                    "completed": lesson_progress is not None and lesson_progress.get("estimate") is not None,
                    "estimate": lesson_progress.get("estimate") if lesson_progress else None
                }
            })
        
        return {
            "user_course": user_course,
            "course": course,
            "lessons": lessons_with_progress
        }

    #async def get_course_with_lessons_and_progress(self, user_course_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить курс с уроками и прогрессом пользователя"""
        result = await self.db.execute(
            select(UserCourse, Course, Lesson)
            .join(Course, UserCourse.course_id == Course.uuid)
            .join(Lesson, Course.uuid == Lesson.course_id)
            .where(UserCourse.uuid == user_course_id)
        )
        
        rows = result.all()
        if not rows:
            return None
        
        # Структурируем данные
        course_data = None
        lessons_with_progress = []
        
        for row in rows:
            user_course, course, lesson = row
            
            if not course_data:
                course_data = {
                    "course": course.to_dict(),
                    "user_course": user_course.to_dict()
                }
            
            # Находим оценку для этого урока в прогрессе пользователя
            lesson_progress = None
            for progress_item in user_course.progress or []:
                if progress_item.get("lesson_id") == str(lesson.uuid):
                    lesson_progress = progress_item
                    break
            
            lessons_with_progress.append({
                "lesson": lesson.to_dict(),
                "progress": lesson_progress
            })
        
        return {
            **course_data,
            "lessons_with_progress": lessons_with_progress
        }
    async def get_course_with_lessons_and_progress(self, user_course_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить курс с уроками и прогрессом пользователя"""
        # Сначала получаем user_course
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
        
        # Затем получаем курс
        course_result = await self.db.execute(
            select(Course).where(Course.uuid == user_course.course_id)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            return None
        
        # Получаем все уроки курса
        lessons_result = await self.db.execute(
            select(Lesson).where(Lesson.course_id == course.uuid)
        )
        lessons = lessons_result.scalars().all()
        
        # Структурируем данные
        course_data = {
            "course": course.to_dict(),
            "user_course": user_course.to_dict()
        }
        
        lessons_with_progress = []
        
        for lesson in lessons:
            # Находим оценку для этого урока в прогрессе пользователя
            lesson_progress = None
            lesson_id_str = str(lesson.uuid)
            
            if user_course.progress:
                for progress_item in user_course.progress:
                    # Преобразуем lesson_id из прогресса для сравнения
                    progress_lesson_id = progress_item.get("lesson_id")
                    if isinstance(progress_lesson_id, UUID):
                        progress_lesson_id = str(progress_lesson_id)
                    
                    if progress_lesson_id == lesson_id_str:
                        lesson_progress = progress_item
                        break
            
            lessons_with_progress.append({
                "lesson": lesson.to_dict(),
                "progress": lesson_progress
            })
        
        return {
            **course_data,
            "lessons_with_progress": lessons_with_progress
        }
        
        
    async def delete(self, user_course_id: UUID) -> bool:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return False
        
        await self.db.delete(user_course)
        await self.db.commit()
        return True
    
    #async def delete(self, user_course_id: UUID) -> UserCourse | None:
        user_course = await self.get_by_id(user_course_id)
        if user_course:
            user_course.archived = True
            await self.db.commit()
            await self.db.refresh(user_course)
        return user_course
    
    
async def get_user_course_repository(
    db: AsyncSession = Depends(get_session),
) -> UserCourseRepository:
    return UserCourseRepository(db)