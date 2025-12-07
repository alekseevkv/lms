from typing import List, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.course import Course
from src.models.lesson import Lesson
from src.repositories.user_course import UserCourseRepository, get_user_course_repository
from src.repositories.course import CourseRepository, get_course_repository
from src.repositories.lesson import LessonRepository, get_lesson_repository
from src.schemas.user_course_schema import (
    UserCourseResponse,
    UserCourseCreate,
    CourseWithProgressResponse,
    UserCourseDetailedResponse,
    StartLessonResponse,
    CompleteLessonRequest,
    LessonProgress
)


class UserCourseService:
    def __init__(
        self,
        user_course_repo: UserCourseRepository,
        course_repo: CourseRepository,
        lesson_repo: LessonRepository
    ):
        self.user_course_repo = user_course_repo
        self.course_repo = course_repo
        self.lesson_repo = lesson_repo

    async def get_user_courses(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CourseWithProgressResponse]:
        """Получить все курсы пользователя с прогрессом"""
        user_courses = await self.user_course_repo.get_all_by_user(
            user_id, skip=skip, limit=limit
        )
        
        if not user_courses:
            return []
        
        result = []
        for user_course in user_courses:
            course = await self.course_repo.get_by_id(user_course.course_id)
            if course:
                result.append(CourseWithProgressResponse(
                    uuid=course.uuid,
                    name=course.name,
                    desc=course.desc,
                    user_progress=user_course
                ))
        
        return result

    async def get_user_course_by_id(
        self, 
        user_course_id: UUID, 
        current_user: User
    ) -> UserCourseDetailedResponse:
        """Получить детальную информацию о курсе пользователя с уроками и прогрессом"""
        # Проверяем права доступа
        user_course = await self.user_course_repo.get_by_id(user_course_id)
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found",
            )
        
        if user_course.user_id != current_user.uuid and "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user course",
            )
        
        # Получаем детальную информацию
        course_data = await self.user_course_repo.get_course_with_progress(user_course_id)
        if not course_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course data not found",
            )
        
        return UserCourseDetailedResponse(
            user_course=course_data["user_course"],
            course=course_data["course"].to_dict(),
            lessons=course_data["lessons"]
        )

    async def enroll_in_course(
        self, 
        course_id: UUID, 
        current_user: User
    ) -> UserCourseResponse:
        """Записать пользователя на курс"""
        # Проверяем существование курса
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        
        # Проверяем, не записан ли уже пользователь
        existing = await self.user_course_repo.get_by_user_and_course(
            current_user.uuid, course_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course",
            )
        
        # Создаем запись о курсе пользователя
        user_course = await self.user_course_repo.create({
            "user_id": current_user.uuid,
            "course_id": course_id,
            "progress": {"lessons": []},
            "total_progress": 0.0
        })
        
        return user_course

    async def start_lesson(
        self, 
        lesson_id: UUID, 
        current_user: User
    ) -> StartLessonResponse:
        """Пользователь начал проходить урок"""
        # Получаем урок
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )
        
        # Получаем курс пользователя
        user_course = await self.user_course_repo.get_by_user_and_course(
            current_user.uuid, lesson.course_id
        )
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not enrolled in this course",
            )
        
        # Отмечаем урок как начатый
        progress = await self.user_course_repo.start_lesson(
            user_course.uuid, lesson_id
        )
        
        # Получаем информацию о прогрессе урока
        lesson_progress = await self.user_course_repo.get_lesson_progress(
            user_course.uuid, lesson_id
        )
        
        lesson_with_progress = {
            "uuid": lesson.uuid,
            "name": lesson.name,
            "desc": lesson.desc,
            "content": lesson.content,
            "video_url": lesson.video_url,
            "course_id": lesson.course_id,
            "progress": {
                "started": lesson_progress.started if lesson_progress else False,
                "completed": lesson_progress.completed if lesson_progress else False,
                "estimate": lesson_progress.estimate if lesson_progress else None
            }
        }
        
        return StartLessonResponse(
            lesson=lesson_with_progress,
            started=True
        )

    async def complete_lesson(
        self, 
        lesson_id: UUID, 
        request: CompleteLessonRequest,
        current_user: User
    ) -> Dict[str, Any]:
        """Завершить урок с оценкой (урок считается пройденным при отправке теста)"""
        # Получаем урок
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )
        
        # Получаем курс пользователя
        user_course = await self.user_course_repo.get_by_user_and_course(
            current_user.uuid, lesson.course_id
        )
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not enrolled in this course",
            )
        
        # Отмечаем урок как завершенный
        progress = await self.user_course_repo.complete_lesson(
            user_course.uuid, lesson_id, request.estimate
        )
        
        # Обновляем прогресс в JSON поле
        lessons_progress = user_course.progress.get("lessons", [])
        
        # Ищем существующую запись
        existing_index = next(
            (i for i, item in enumerate(lessons_progress) 
             if str(item.get("lesson_id")) == str(lesson_id)),
            None
        )
        
        if existing_index is not None:
            # Обновляем существующую запись
            lessons_progress[existing_index]["estimate"] = request.estimate
        else:
            # Добавляем новую запись
            lessons_progress.append({
                "lesson_id": lesson_id,
                "estimate": request.estimate
            })
        
        # Обновляем прогресс курса
        user_course.progress["lessons"] = lessons_progress
        user_course.update_progress()
        
        await self.user_course_repo.update(
            user_course.uuid, 
            {"progress": user_course.progress, "total_progress": user_course.total_progress}
        )
        
        return {
            "message": "Lesson completed successfully",
            "lesson_id": lesson_id,
            "estimate": request.estimate,
            "progress": user_course.total_progress
        }

    async def get_user_course_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Получить статистику по курсам пользователя"""
        user_courses = await self.user_course_repo.get_all_by_user(user_id)
        
        total_courses = len(user_courses)
        completed_courses = sum(1 for uc in user_courses if uc.total_progress == 100)
        in_progress_courses = sum(1 for uc in user_courses if 0 < uc.total_progress < 100)
        
        return {
            "total_courses": total_courses,
            "completed_courses": completed_courses,
            "in_progress_courses": in_progress_courses,
            "average_progress": sum(uc.total_progress for uc in user_courses) / total_courses if total_courses > 0 else 0
        }


async def get_user_course_service(
    user_course_repo: UserCourseRepository = Depends(get_user_course_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
    lesson_repo: LessonRepository = Depends(get_lesson_repository),
) -> UserCourseService:
    return UserCourseService(user_course_repo, course_repo, lesson_repo)